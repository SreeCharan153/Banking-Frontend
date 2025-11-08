'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { atmApi } from '@/lib/api';

export function CreateUser() {
  const [form, setForm] = useState({ un: '', pas: '', vps: '', role: 'teller' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm(prev => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const res = await atmApi.createUser(form);
      setSuccess(res.message || "User created");
      setForm({ un: '', pas: '', vps: '', role: 'teller' });
    } catch (err: any) {
      setError(err.message || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold text-gray-800">Create New User</h2>

      <Input placeholder="Username" value={form.un} onChange={handleChange('un')} required />

      <Input type="password" placeholder="Password" value={form.pas} onChange={handleChange('pas')} required />

      <Input type="password" placeholder="Verify Password" value={form.vps} onChange={handleChange('vps')} required />

      <select
        className="w-full border p-2 rounded"
        value={form.role}
        onChange={handleChange('role')}
      >
        <option value="admin">Admin</option>
        <option value="teller">Teller</option>
        <option value="customer">Customer</option>
      </select>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-emerald-100 border-emerald-200 text-emerald-800">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <Button disabled={loading} className="w-full">
        {loading ? "Creating..." : "Create User"}
      </Button>
    </form>
  );
}
