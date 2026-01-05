import { Link, useLocation } from 'react-router-dom';
import { ShoppingCart, Bell, Plus, Home } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { getAlerts } from '../api';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const { data: alerts } = useQuery({
    queryKey: ['alerts', true],
    queryFn: () => getAlerts(true),
  });

  const unreadCount = alerts?.length || 0;

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/add-item', icon: Plus, label: 'Add Item' },
    { path: '/alerts', icon: Bell, label: 'Alerts', badge: unreadCount },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-2">
              <ShoppingCart className="w-8 h-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                Price Tracker
              </span>
            </Link>

            <nav className="flex space-x-4">
              {navItems.map(({ path, icon: Icon, label, badge }) => (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors relative ${
                    location.pathname === path
                      ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{label}</span>
                  {badge !== undefined && badge > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {badge}
                    </span>
                  )}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
