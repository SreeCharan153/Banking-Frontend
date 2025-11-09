'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { KeyRound, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { atmApi } from '@/lib/api';

export function ChangePinForm() {
  const [formData, setFormData] = useState({
    h: '',
    oldPin: '',
    newPin: '',
    confirmPin: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    // Client-side validation
    if (formData.newPin !== formData.confirmPin) {
      setError('New PIN and confirmation PIN do not match');
      setIsLoading(false);
      return;
    }

    if (formData.newPin.length !== 4 || !formData.newPin.match(/^\d{4}$/)) {
      setError('New PIN must be exactly 4 digits');
      setIsLoading(false);
      return;
    }

    if (formData.newPin === formData.oldPin) {
      setError('New PIN cannot be the same as the old PIN');
      setIsLoading(false);
      return;
    }

    try {
      const changePinData = {
        h: formData.h,
        oldpin: formData.oldPin,
        newpin: formData.newPin,
        vnewpin: formData.confirmPin,
      };

      const result = await atmApi.changePin(changePinData) as { message: string };
      setSuccess(result.message);
      setFormData({ h: '', oldPin: '', newPin: '', confirmPin: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'PIN change failed');
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
      <CardHeader className="bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-t-lg">
        <div className="flex items-center space-x-3">
          <KeyRound className="h-6 w-6" />
          <div>
            <CardTitle className="text-xl">Change PIN</CardTitle>
            <CardDescription className="text-orange-100">
              Update your account PIN for security
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
            <Label htmlFor="old-pin" className="text-sm font-medium">
              Current PIN
            </Label>
            <Input
              id="old-pin"
              type="password"
              value={formData.oldPin}
              onChange={handleChange('oldPin')}
              placeholder="••••"
              maxLength={4}
              pattern="[0-9]{4}"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="new-pin" className="text-sm font-medium">
                New PIN
              </Label>
              <Input
                id="new-pin"
                type="password"
                value={formData.newPin}
                onChange={handleChange('newPin')}
                placeholder="••••"
                maxLength={4}
                pattern="[0-9]{4}"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-pin" className="text-sm font-medium">
                Confirm New PIN
              </Label>
              <Input
                id="confirm-pin"
                type="password"
                value={formData.confirmPin}
                onChange={handleChange('confirmPin')}
                placeholder="••••"
                maxLength={4}
                pattern="[0-9]{4}"
                required
              />
            </div>
          </div>

          {/* PIN Strength Indicator */}
          {formData.newPin && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <h4 className="font-medium text-orange-900 mb-2">PIN Requirements</h4>
              <div className="space-y-1 text-sm">
                <div className={`flex items-center ${formData.newPin.length === 4 ? 'text-emerald-600' : 'text-gray-500'}`}>
                  <span className="mr-2">{formData.newPin.length === 4 ? '✓' : '○'}</span>
                  Exactly 4 digits
                </div>
                <div className={`flex items-center ${formData.newPin.match(/^\d+$/) ? 'text-emerald-600' : 'text-gray-500'}`}>
                  <span className="mr-2">{formData.newPin.match(/^\d+$/) ? '✓' : '○'}</span>
                  Numbers only
                </div>
                <div className={`flex items-center ${formData.newPin !== formData.oldPin && formData.newPin ? 'text-emerald-600' : 'text-gray-500'}`}>
                  <span className="mr-2">{formData.newPin !== formData.oldPin && formData.newPin ? '✓' : '○'}</span>
                  Different from current PIN
                </div>
                <div className={`flex items-center ${formData.newPin === formData.confirmPin && formData.newPin ? 'text-emerald-600' : 'text-gray-500'}`}>
                  <span className="mr-2">{formData.newPin === formData.confirmPin && formData.newPin ? '✓' : '○'}</span>
                  PINs match
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
            className="w-full bg-orange-600 hover:bg-orange-700 transition-all duration-200"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Changing PIN...
              </>
            ) : (
              'Change PIN'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}