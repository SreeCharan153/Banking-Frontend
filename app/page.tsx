'use client';

import { useState } from 'react';
import { PasswordAuth } from '@/components/PasswordAuth';
import { ATMDashboard } from '@/components/ATMDashboard';

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  if (!isAuthenticated) {
    return <PasswordAuth onAuthenticated={() => setIsAuthenticated(true)} />;
  }

  return <ATMDashboard />;
}