'use client';

import { useEffect, useState } from 'react';
import { PasswordAuth } from '@/components/PasswordAuth';
import { ATMDashboard } from '@/components/ATMDashboard';
import { API_BASE_URL } from '@/lib/config';

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [role, setRole] = useState<string | null>(null);

const checkAuth = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/check`, { credentials: "include" });

    if (!res.ok) {
      setIsAuthenticated(false);
      setRole(null);
      return;
    }

    const data = await res.json();
    setIsAuthenticated(true);
    setRole(data.role);
  } catch {
    setIsAuthenticated(false);
    setRole(null);
  }
};

  useEffect(() => {
    checkAuth();
  }, []);

  if (isAuthenticated === null) return <div>Loading...</div>;

  if (!isAuthenticated)
    return (
      <PasswordAuth
        onAuthenticated={(newRole) => {
          setIsAuthenticated(true);
          setRole(newRole);
        }}
      />
    );

  return (
    <ATMDashboard
      role={role || "teller"}
      onLogout={() => {
        setIsAuthenticated(false);
        setRole(null);
      }}
    />
  );
}
