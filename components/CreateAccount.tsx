'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { UserPlus, Loader2, CheckCircle2 } from 'lucide-react';
import { atmApi } from '@/lib/api';

export function CreateAccount() {
  const [formData, setFormData] = useState({
    h: '',
    pin: '',
    mobileno: '',
    gmail: '',
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
      const result = await atmApi.createAccount(formData);
      setSuccess(result.message);
      setFormData({ h: '', pin: '', mobileno: '', gmail: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Account creation failed');
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
      <CardHeader className="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-t-lg">
        <div className="flex items-center space-x-3">
          <UserPlus className="h-6 w-6" />
          <div>
            <CardTitle className="text-xl">Create New Account</CardTitle>
            <CardDescription className="text-emerald-100">
              Register a new ATM account holder
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="holder" className="text-sm font-medium">
                Account Holder Name
              </Label>
              <Input
                id="holder"
                type="text"
                value={formData.h}
                onChange={handleChange('h')}
                placeholder="Full name"
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
                placeholder="1234"
                maxLength={4}
                pattern="[0-9]{4}"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="mobile" className="text-sm font-medium">
                Mobile Number
              </Label>
              <Input
                id="mobile"
                type="tel"
                value={formData.mobileno}
                onChange={handleChange('mobileno')}
                placeholder="9876543210"
                maxLength={10}
                pattern="[0-9]{10}"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                value={formData.gmail}
                onChange={handleChange('gmail')}
                placeholder="user@example.com"
                required
              />
            </div>
          </div>

          {error && (
            <Alert variant="destructive" className="animate-in fade-in-0">
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
            className="w-full bg-emerald-600 hover:bg-emerald-700 transition-all duration-200"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}