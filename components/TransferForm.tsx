'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowRightLeft, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { atmApi } from '@/lib/api';

export function TransferForm() {
  const [formData, setFormData] = useState({
    h: '',
    pin: '',
    toAccount: '',
    amount: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const transferData = {
        h: formData.h,
        pin: parseInt(formData.pin),
        toAccount: formData.toAccount, // Keep the form field name for UI consistency
        amount: parseInt(formData.amount),
      };

      const result = await atmApi.transfer(transferData);
      // Assert result type to access message property
      setSuccess((result as { message: string }).message);
      setFormData({ h: '', pin: '', toAccount: '', amount: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Transfer failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  return (
    <Card className="shadow-lg border-0 bg-white">
      <CardHeader className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-t-lg">
        <div className="flex items-center space-x-3">
          <ArrowRightLeft className="h-6 w-6" />
          <div>
            <CardTitle className="text-xl">Transfer Money</CardTitle>
            <CardDescription className="text-purple-100">
              Transfer funds between accounts
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="from-account" className="text-sm font-medium">
                From Account Number
              </Label>
              <Input
                id="from-account"
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
              <Label htmlFor="to-account" className="text-sm font-medium">
                To Account Number
              </Label>
              <Input
                id="to-account"
                type="text"
                value={formData.toAccount}
                onChange={handleChange('toAccount')}
                placeholder="e.g., AC1002"
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
          </div>

          {/* Transfer Summary */}
          {formData.h && formData.toAccount && formData.amount && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h4 className="font-medium text-purple-900 mb-2">Transfer Summary</h4>
              <div className="space-y-1 text-sm text-purple-800">
                <div className="flex justify-between">
                  <span>From:</span>
                  <span className="font-mono">{formData.h}</span>
                </div>
                <div className="flex justify-between">
                  <span>To:</span>
                  <span className="font-mono">{formData.toAccount}</span>
                </div>
                <div className="flex justify-between font-medium">
                  <span>Amount:</span>
                  <span>₹{formData.amount}</span>
                </div>
              </div>
            </div>
          )}

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
            className="w-full bg-purple-600 hover:bg-purple-700 transition-all duration-200"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing Transfer...
              </>
            ) : (
              'Transfer Money'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}