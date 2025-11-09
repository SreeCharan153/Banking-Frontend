'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { atmApi } from '@/lib/api';

export function CreateUser() {
  const [form, setForm] = useState({ username: '', pas: '', vps: '', role: 'teller' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange =
    (field: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (form.pas !== form.vps) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const res = await atmApi.createUser(form);
      setSuccess(res.message || 'User created.');

      // reset form
      setForm({ username: '', pas: '', vps: '', role: 'teller' });
    } catch (err: any) {
      setError(err.message || 'Failed to create user.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-xl shadow-md">
      <h2 className="text-xl font-bold text-gray-900">Create New User</h2>

      <Input
        placeholder="Username"
        value={form.username}
        onChange={handleChange('username')}
        required
      />

      <Input
        type="password"
        placeholder="Password"
        value={form.pas}
        onChange={handleChange('pas')}
        required
      />

      <Input
        type="password"
        placeholder="Verify Password"
        value={form.vps}
        onChange={handleChange('vps')}
        required
      />

      <Select
        value={form.role}
        onValueChange={val => setForm(prev => ({ ...prev, role: val }))}
      >
        <SelectTrigger>
          <SelectValue placeholder="Select role" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="admin">Admin</SelectItem>
          <SelectItem value="teller">Teller</SelectItem>
          <SelectItem value="customer">Customer</SelectItem>
        </SelectContent>
      </Select>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-emerald-200 border border-emerald-300 text-emerald-800">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <Button disabled={loading} className="w-full">
        {loading ? 'Creating...' : 'Create User'}
      </Button>
    </form>
  );
}
