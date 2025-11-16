'use client';

import { useEffect, useState } from 'react';
import { PasswordAuth } from '@/components/PasswordAuth';
import { ATMDashboard } from '@/components/ATMDashboard';
import { API_BASE_URL } from '@/lib/config';

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);

const checkAuth = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/check`, { credentials: "include" });

    if (!res.ok) {
      setIsAuthenticated(false);
      setRole(null);
      setUserName(null);
      return;
    }

    const data = await res.json();
    setIsAuthenticated(true);
    setRole(data.role);
    setUserName(data.user_name);
  } catch {
    setIsAuthenticated(false);
    setRole(null);
    setUserName(null);
  }
};

  useEffect(() => {
    checkAuth();
  }, []);


  if (!isAuthenticated)
    return (
      <PasswordAuth
        onAuthenticated={(newRole, newUserName) => {
          setIsAuthenticated(true);
          setRole(newRole);
          setUserName(newUserName);
        }}
      />
    );

  return (
    <ATMDashboard
      role={role || "teller"}
      userName={userName || "User"}
      onLogout={() => {
        setIsAuthenticated(false);
        setRole(null);
        setUserName(null);
      }}
    />
  );
}
