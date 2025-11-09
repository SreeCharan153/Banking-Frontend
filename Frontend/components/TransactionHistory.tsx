'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { History as HistoryIcon, Loader2, AlertCircle, ArrowUpCircle, ArrowDownCircle, ArrowRightLeft, Calendar, IndianRupee, RefreshCw } from 'lucide-react';
import { atmApi } from '@/lib/api';

export type HistoryEntryTuple = [number, string, string, number, string];
export type HistorySuccess = { history: HistoryEntryTuple[] };
export type HistoryError = { message?: string; detail?: string };
export type HistoryResponse = HistorySuccess | HistoryError;

function isHistorySuccess(v: unknown): v is HistorySuccess {
  return !!v && typeof v === 'object' && 'history' in (v as any) && Array.isArray((v as any).history);
}

function normalizeAction(raw: string): 'deposit' | 'withdraw' | 'transfer_in' | 'transfer_out' | 'other' {
  const s = raw.toLowerCase();
  if (s.includes('deposit')) return 'deposit';
  if (s.includes('withdraw')) return 'withdraw';
  if (s.includes('received')) return 'transfer_in';
  if (s.includes('transfer')) return 'transfer_out';
  return 'other';
}

export function TransactionHistory() {
  const [formData, setFormData] = useState({ accountNumber: '', pin: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [transactions, setTransactions] = useState<HistoryEntryTuple[]>([]);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError('');

    try {
      const payload = { h: formData.accountNumber.trim(), pin: formData.pin.trim() };
      const result: unknown = await atmApi.history(payload);

      if (isHistorySuccess(result)) {
        setTransactions(result.history);
        if (result.history.length === 0) {
          setError('No transaction history found for this account.');
        }
      } else {
        const msg = (result as HistoryError)?.message || (result as HistoryError)?.detail || 'Failed to fetch transaction history.';
        setError(msg);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch transaction history.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTransactions([]);
    await fetchHistory();
  };

  const handleRefresh = async () => {
    await fetchHistory();
  };

  const handleChange = (field: keyof typeof formData) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  const getTransactionIcon = (action: string) => {
    switch (normalizeAction(action)) {
      case 'deposit':
        return <ArrowDownCircle className="h-4 w-4" />;
      case 'withdraw':
        return <ArrowUpCircle className="h-4 w-4" />;
      case 'transfer_in':
        return <ArrowRightLeft className="h-4 w-4" />;
      case 'transfer_out':
        return <ArrowRightLeft className="h-4 w-4" />;
      default:
        return <IndianRupee className="h-4 w-4" />;
    }
  };

  const getTransactionColor = (action: string) => {
    switch (normalizeAction(action)) {
      case 'deposit':
      case 'transfer_in':
        return 'text-emerald-600';
      case 'withdraw':
      case 'transfer_out':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const formatDate = (timestamp: string) => {
    const d = new Date(timestamp.replace(' ', 'T'));
    return isNaN(d.getTime())
      ? timestamp
      : d.toLocaleString('en-IN', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const formatAmount = (amount: number, action: string) => {
    const kind = normalizeAction(action);
    const isCredit = kind === 'deposit' || kind === 'transfer_in';
    const prefix = isCredit ? '+' : '-';
    return `${prefix}₹${Math.abs(amount).toLocaleString('en-IN')}`;
  };

  const formDisabled = isLoading || formData.accountNumber.trim().length === 0 || formData.pin.trim().length !== 4;

  return (
    <Card className="shadow-lg border-0 bg-white">
      <CardHeader className="bg-gradient-to-r from-slate-600 to-slate-700 text-white rounded-t-lg">
        <div className="flex items-center space-x-3">
          <HistoryIcon className="h-6 w-6" />
          <div>
            <CardTitle className="text-xl">Transaction History</CardTitle>
            <CardDescription className="text-slate-200">View your account transaction history</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="account" className="text-sm font-medium">Account Number</Label>
              <Input
                id="account"
                type="text"
                value={formData.accountNumber}
                onChange={handleChange('accountNumber')}
                placeholder="e.g., AC10000000001"
                required
                autoComplete="off"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="pin" className="text-sm font-medium">4-Digit PIN</Label>
              <Input
                id="pin"
                type="password"
                inputMode="numeric"
                value={formData.pin}
                onChange={handleChange('pin')}
                placeholder="••••"
                maxLength={4}
                pattern="[0-9]{4}"
                required
                autoComplete="off"
              />
            </div>
          </div>

          <div className="flex space-x-2">
            <Button type="submit" className="flex-1 bg-slate-600 hover:bg-slate-700 transition-all duration-200" disabled={formDisabled}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading History...
                </>
              ) : (
                <>
                  <HistoryIcon className="mr-2 h-4 w-4" /> Get Transaction History
                </>
              )}
            </Button>

            {transactions.length > 0 && (
              <Button type="button" onClick={handleRefresh} className="bg-emerald-600 hover:bg-emerald-700" disabled={isLoading}>
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              </Button>
            )}
          </div>
        </form>

        {error && (
          <Alert variant="destructive" className="animate-in fade-in-0 mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {transactions.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Transaction History for {formData.accountNumber}</h3>
              <span className="text-sm text-gray-500">{transactions.length} transaction{transactions.length !== 1 ? 's' : ''}</span>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {transactions.map((transaction) => (
                <div key={transaction[0]} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    {getTransactionIcon(transaction[2])}
                    <div>
                      <div className="font-medium text-gray-900 capitalize">{transaction[2]}</div>
                      <div className="flex items-center text-xs text-gray-500 mt-1">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(transaction[4])}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-semibold ${getTransactionColor(transaction[2])}`}>
                      {formatAmount(transaction[3], transaction[2])}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
