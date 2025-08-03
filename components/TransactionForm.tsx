'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowDownCircle, ArrowUpCircle, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { atmApi } from '@/lib/api';

interface TransactionFormProps {
  type: 'deposit' | 'withdraw';
}

export function TransactionForm({ type }: TransactionFormProps) {
  const [formData, setFormData] = useState({
    h: '',
    pin: '',
    amount: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const isDeposit = type === 'deposit';
  const icon = isDeposit ? ArrowDownCircle : ArrowUpCircle;
  const bgColor = isDeposit ? 'from-emerald-500 to-emerald-600' : 'from-red-500 to-red-600';
  const buttonColor = isDeposit ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-red-600 hover:bg-red-700';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const transactionData = {
        h: formData.h,
        pin: parseInt(formData.pin),
        amount: parseInt(formData.amount),
      };

      const result = isDeposit
        ? await atmApi.deposit(transactionData)
        : await atmApi.withdraw(transactionData);

      setSuccess(result.message);
      setFormData({ h: '', pin: '', amount: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Transaction failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  const Icon = icon;

  return (
    <Card className="shadow-lg border-0 bg-white">
      <CardHeader className={`bg-gradient-to-r ${bgColor} text-white rounded-t-lg`}>
        <div className="flex items-center space-x-3">
          <Icon className="h-6 w-6" />
          <div>
            <CardTitle className="text-xl capitalize">{type} Money</CardTitle>
            <CardDescription className="text-white/90">
              {isDeposit ? 'Add funds to your account' : 'Withdraw funds from your account'}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="account" className="text-sm font-medium">
              Account Number
            </Label>
            <Input
              id="account"
              type="text"
              value={formData.h}
              onChange={handleChange('h')}
              placeholder="e.g., AC1001"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="pin" className="text-sm font-medium">
              4-Digit PIN
            </Label>
            <Input
              id="pin"
              type="password"
              value={formData.pin}
              onChange={handleChange('pin')}
              placeholder="••••"
              maxLength={4}
              pattern="[0-9]{4}"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="amount" className="text-sm font-medium">
              Amount (₹)
            </Label>
            <Input
              id="amount"
              type="number"
              value={formData.amount}
              onChange={handleChange('amount')}
              placeholder="0"
              min="1"
              required
            />
          </div>

          {error && (
            <Alert variant="destructive" className="animate-in fade-in-0">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="border-emerald-200 bg-emerald-50 text-emerald-800 animate-in fade-in-0">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          <Button
            type="submit"
            className={`w-full ${buttonColor} transition-all duration-200`}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              `${isDeposit ? 'Deposit' : 'Withdraw'} Money`
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}