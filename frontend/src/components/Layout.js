import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  HomeIcon,
  UserGroupIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  AcademicCapIcon,
  ChatBubbleLeftRightIcon,
  DocumentChartBarIcon,
  PhoneIcon,
  UsersIcon,
  ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const location = useLocation();

  const getNavigationForRole = (role) => {
    const baseNavigation = [
      { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, roles: ['student', 'mentor', 'admin'] },
    ];

    if (role === 'student') {
      return [
        ...baseNavigation,
        { name: 'Progress Report', href: '#', icon: DocumentChartBarIcon, roles: ['student'], action: 'progress' },
        { name: 'Contact Mentor', href: '#', icon: PhoneIcon, roles: ['student'], action: 'contact' },
        { name: 'AI Assistant', href: '#', icon: ChatBubbleLeftRightIcon, roles: ['student'], action: 'chat' },
        { name: 'Academic Resources', href: '#', icon: AcademicCapIcon, roles: ['student'], action: 'resources' },
        { name: 'Settings', href: '/settings', icon: Cog6ToothIcon, roles: ['student'] },
      ];
    }

    if (role === 'mentor') {
      return [
        ...baseNavigation,
        { name: 'My Students', href: '#', icon: UsersIcon, roles: ['mentor'], action: 'students' },
        { name: 'Alert Management', href: '#', icon: ExclamationTriangleIcon, roles: ['mentor'], action: 'alerts' },
        { name: 'Performance Analytics', href: '#', icon: ChartBarIcon, roles: ['mentor'], action: 'analytics' },
        { name: 'Student Communications', href: '#', icon: ChatBubbleLeftRightIcon, roles: ['mentor'], action: 'communications' },
        { name: 'Settings', href: '/settings', icon: Cog6ToothIcon, roles: ['mentor'] },
      ];
    }

    if (role === 'admin') {
      return [
        ...baseNavigation,
        { name: 'Manage Students', href: '#', icon: UserGroupIcon, roles: ['admin'], action: 'manage-students' },
        { name: 'Alert Management', href: '#', icon: ExclamationTriangleIcon, roles: ['admin'], action: 'manage-alerts' },
        { name: 'System Analytics', href: '#', icon: ChartBarIcon, roles: ['admin'], action: 'system-analytics' },
        { name: 'Mentor Management', href: '#', icon: UsersIcon, roles: ['admin'], action: 'manage-mentors' },
        { name: 'System Settings', href: '#', icon: Cog6ToothIcon, roles: ['admin'], action: 'system-settings' },
        { name: 'Reports & Exports', href: '#', icon: ClipboardDocumentListIcon, roles: ['admin'], action: 'reports' },
      ];
    }

    return baseNavigation;
  };

  const navigation = getNavigationForRole(user?.role);

  const filteredNavigation = navigation;

  const handleNavClick = (item, e) => {
    if (item.action) {
      e.preventDefault();
      // Dispatch custom events that dashboards can listen to
      window.dispatchEvent(new CustomEvent('sidebarAction', {
        detail: { action: item.action, role: user?.role }
      }));
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <motion.div
        initial={false}
        animate={sidebarOpen ? { x: 0 } : { x: '-100%' }}
        transition={{ type: 'tween', duration: 0.3 }}
        className="fixed inset-0 z-50 lg:hidden"
      >
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white">
          <div className="flex h-16 items-center justify-between px-4">
            <h1 className="text-xl font-bold text-gray-900">Dropout Prevention</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4">
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`${
                    isActive
                      ? 'bg-primary-50 border-r-2 border-primary-600 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  } group flex items-center px-2 py-2 text-sm font-medium rounded-md`}
                  onClick={(e) => {
                    setSidebarOpen(false);
                    handleNavClick(item, e);
                  }}
                >
                  <item.icon
                    className={`${
                      isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                    } mr-3 h-6 w-6`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                  <span className="text-sm font-medium text-white">
                    {user?.name?.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">{user?.name}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="mt-3 w-full flex items-center px-2 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
            >
              <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5" />
              Sign out
            </button>
          </div>
        </div>
      </motion.div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
          <div className="flex items-center h-16 px-4 border-b border-gray-200">
            <h1 className="text-xl font-bold text-gray-900">Dropout Prevention</h1>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4">
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`${
                    isActive
                      ? 'bg-primary-50 border-r-2 border-primary-600 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  } group flex items-center px-2 py-2 text-sm font-medium rounded-md`}
                  onClick={(e) => handleNavClick(item, e)}
                >
                  <item.icon
                    className={`${
                      isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                    } mr-3 h-6 w-6`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                  <span className="text-sm font-medium text-white">
                    {user?.name?.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">{user?.name}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="mt-3 w-full flex items-center px-2 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
            >
              <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5" />
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 bg-white border-b border-gray-200">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-gray-500 hover:text-gray-600"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            
            <div className="flex items-center space-x-4">
              <button className="text-gray-400 hover:text-gray-500">
                <BellIcon className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
