'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Smartphone, Mail, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { atmApi } from '@/lib/api';

export function UpdateInfo() {
  const [mobileForm, setMobileForm] = useState({
    h: '',
    pin: '',
    nmobile: '',
    omobile: '',
  });

  const [emailForm, setEmailForm] = useState({
    h: '',
    pin: '',
    nemail: '',
    oemail: '',
  });

  const [mobileLoading, setMobileLoading] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [mobileError, setMobileError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [mobileSuccess, setMobileSuccess] = useState('');
  const [emailSuccess, setEmailSuccess] = useState('');

  const handleMobileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMobileLoading(true);
    setMobileError('');
    setMobileSuccess('');

    try {
      const result = await atmApi.updateMobile({
        h: mobileForm.h,
        pin: parseInt(mobileForm.pin),
        nmobile: mobileForm.nmobile,
        omobile: mobileForm.omobile,
      });
      setMobileSuccess(result.message);
      setMobileForm({ h: '', pin: '', nmobile: '', omobile: '' });
    } catch (err) {
      setMobileError(err instanceof Error ? err.message : 'Update failed');
    } finally {
      setMobileLoading(false);
    }
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailLoading(true);
    setEmailError('');
    setEmailSuccess('');

    try {
      const result = await atmApi.updateEmail({
        h: emailForm.h,
        pin: parseInt(emailForm.pin),
        nemail: emailForm.nemail,
        oemail: emailForm.oemail,
      });
      setEmailSuccess(result.message);
      setEmailForm({ h: '', pin: '', nemail: '', oemail: '' });
    } catch (err) {
      setEmailError(err instanceof Error ? err.message : 'Update failed');
    } finally {
      setEmailLoading(false);
    }
  };

  return (
    <Card className="shadow-lg border-0 bg-white">
      <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-t-lg">
        <CardTitle className="text-xl">Update Account Information</CardTitle>
        <CardDescription className="text-blue-100">
          Update your mobile number or email address
        </CardDescription>
      </CardHeader>
      <CardContent className="p-6">
        <Tabs defaultValue="mobile" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="mobile" className="flex items-center space-x-2">
              <Smartphone className="h-4 w-4" />
              <span>Mobile</span>
            </TabsTrigger>
            <TabsTrigger value="email" className="flex items-center space-x-2">
              <Mail className="h-4 w-4" />
              <span>Email</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="mobile">
            <form onSubmit={handleMobileSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="m-account" className="text-sm font-medium">
                    Account Number
                  </Label>
                  <Input
                    id="m-account"
                    type="text"
                    value={mobileForm.h}
                    onChange={(e) => setMobileForm(prev => ({ ...prev, h: e.target.value }))}
                    placeholder="e.g., AC1001"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="m-pin" className="text-sm font-medium">
                    PIN
                  </Label>
                  <Input
                    id="m-pin"
                    type="password"
                    value={mobileForm.pin}
                    onChange={(e) => setMobileForm(prev => ({ ...prev, pin: e.target.value }))}
                    placeholder="••••"
                    maxLength={4}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="old-mobile" className="text-sm font-medium">
                    Current Mobile
                  </Label>
                  <Input
                    id="old-mobile"
                    type="tel"
                    value={mobileForm.omobile}
                    onChange={(e) => setMobileForm(prev => ({ ...prev, omobile: e.target.value }))}
                    placeholder="9876543210"
                    maxLength={10}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new-mobile" className="text-sm font-medium">
                    New Mobile
                  </Label>
                  <Input
                    id="new-mobile"
                    type="tel"
                    value={mobileForm.nmobile}
                    onChange={(e) => setMobileForm(prev => ({ ...prev, nmobile: e.target.value }))}
                    placeholder="9876543210"
                    maxLength={10}
                    required
                  />
                </div>
              </div>

              {mobileError && (
                <Alert variant="destructive" className="animate-in fade-in-0">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{mobileError}</AlertDescription>
                </Alert>
              )}

              {mobileSuccess && (
                <Alert className="border-emerald-200 bg-emerald-50 text-emerald-800 animate-in fade-in-0">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  <AlertDescription>{mobileSuccess}</AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 transition-all duration-200"
                disabled={mobileLoading}
              >
                {mobileLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Updating...
                  </>
                ) : (
                  'Update Mobile Number'
                )}
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="email">
            <form onSubmit={handleEmailSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="e-account" className="text-sm font-medium">
                    Account Number
                  </Label>
                  <Input
                    id="e-account"
                    type="text"
                    value={emailForm.h}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, h: e.target.value }))}
                    placeholder="e.g., AC1001"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="e-pin" className="text-sm font-medium">
                    PIN
                  </Label>
                  <Input
                    id="e-pin"
                    type="password"
                    value={emailForm.pin}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, pin: e.target.value }))}
                    placeholder="••••"
                    maxLength={4}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="old-email" className="text-sm font-medium">
                    Current Email
                  </Label>
                  <Input
                    id="old-email"
                    type="email"
                    value={emailForm.oemail}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, oemail: e.target.value }))}
                    placeholder="current@example.com"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new-email" className="text-sm font-medium">
                    New Email
                  </Label>
                  <Input
                    id="new-email"
                    type="email"
                    value={emailForm.nemail}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, nemail: e.target.value }))}
                    placeholder="new@example.com"
                    required
                  />
                </div>
              </div>

              {emailError && (
                <Alert variant="destructive" className="animate-in fade-in-0">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{emailError}</AlertDescription>
                </Alert>
              )}

              {emailSuccess && (
                <Alert className="border-emerald-200 bg-emerald-50 text-emerald-800 animate-in fade-in-0">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  <AlertDescription>{emailSuccess}</AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 transition-all duration-200"
                disabled={emailLoading}
              >
                {emailLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Updating...
                  </>
                ) : (
                  'Update Email Address'
                )}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}