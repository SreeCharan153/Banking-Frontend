'use client';

import { useState } from 'react';
import { CreateAccount } from './CreateAccount';
import { TransactionForm } from './TransactionForm';
import { UpdateInfo } from './UpdateInfo';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  UserPlus, 
  ArrowDownCircle, 
  ArrowUpCircle, 
  Settings,
  Banknote,
  Shield,
  Users
} from 'lucide-react';

type ActiveTab = 'overview' | 'create' | 'deposit' | 'withdraw' | 'update';

export function ATMDashboard() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');

  const menuItems = [
    {
      id: 'create' as const,
      label: 'Create Account',
      icon: UserPlus,
      color: 'bg-emerald-500 hover:bg-emerald-600',
      description: 'Register new account holder'
    },
    {
      id: 'deposit' as const,
      label: 'Deposit Money',
      icon: ArrowDownCircle,
      color: 'bg-emerald-500 hover:bg-emerald-600',
      description: 'Add funds to account'
    },
    {
      id: 'withdraw' as const,
      label: 'Withdraw Money',
      icon: ArrowUpCircle,
      color: 'bg-red-500 hover:bg-red-600',
      description: 'Withdraw funds from account'
    },
    {
      id: 'update' as const,
      label: 'Update Info',
      icon: Settings,
      color: 'bg-blue-500 hover:bg-blue-600',
      description: 'Update mobile or email'
    }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'create':
        return <CreateAccount />;
      case 'deposit':
        return <TransactionForm type="deposit" />;
      case 'withdraw':
        return <TransactionForm type="withdraw" />;
      case 'update':
        return <UpdateInfo />;
      default:
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <Card 
                  key={item.id}
                  className="cursor-pointer hover:shadow-lg transition-all duration-200 border-0 bg-white hover:scale-[1.02]"
                  onClick={() => setActiveTab(item.id)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <div className={`w-12 h-12 rounded-lg ${item.color} flex items-center justify-center transition-colors`}>
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900">{item.label}</h3>
                        <p className="text-sm text-gray-600">{item.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-blue-900 rounded-lg flex items-center justify-center">
                <Banknote className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ATM Management System</h1>
                <p className="text-sm text-gray-600">Secure Banking Operations</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-emerald-500" />
              <span className="text-sm text-gray-600">Authenticated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      {activeTab !== 'overview' && (
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center space-x-1 h-12">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setActiveTab('overview')}
                className="text-blue-600 hover:text-blue-800"
              >
                ← Back to Dashboard
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' ? (
          <div className="space-y-8">
            {/* Welcome Section */}
            <div className="text-center space-y-4">
              <div className="mx-auto w-20 h-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                <Users className="h-10 w-10 text-white" />
              </div>
              <div>
                <h2 className="text-3xl font-bold text-gray-900">Welcome to ATM System</h2>
                <p className="text-lg text-gray-600 mt-2">
                  Manage accounts, process transactions, and update customer information
                </p>
              </div>
            </div>

            {/* Quick Actions */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h3>
              {renderContent()}
            </div>
          </div>
        ) : (
          <div className="max-w-2xl mx-auto">
            {renderContent()}
          </div>
        )}
      </div>
    </div>
  );
}