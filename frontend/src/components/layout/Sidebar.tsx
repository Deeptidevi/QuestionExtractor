import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  HelpCircle,
  CheckSquare,
  KeyRound,
  BarChart3,
  GitFork,
  Settings,
  Code2,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Layers,
  Zap,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useQuery } from '@tanstack/react-query';
import { reviewApi } from '../../api/review';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  setCollapsed,
  mobileOpen,
  setMobileOpen,
}) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Fetch pending review count for badge
  const { data: reviewData } = useQuery({
    queryKey: ['reviewQueueCount'],
    queryFn: () => reviewApi.getReviewQueue({ page_size: 1, status: 'PENDING' }),
    refetchInterval: 10000,
  });

  const pendingCount = reviewData?.meta?.total || 0;

  const mainNav = [
    { name: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
    { name: 'Documents', to: '/documents', icon: FileText },
    { name: 'Questions', to: '/questions', icon: HelpCircle },
    {
      name: 'Review Queue',
      to: '/review',
      icon: CheckSquare,
      badge: pendingCount > 0 ? pendingCount : undefined,
      badgeColor: 'bg-amber-500 text-white shadow-xs animate-pulse',
    },
    { name: 'Answer Keys', to: '/answer-keys', icon: KeyRound },
    { name: 'Relationships', to: '/relationships', icon: GitFork },
    { name: 'Analytics', to: '/analytics', icon: BarChart3 },
  ];

  const secondaryNav = [
    { name: 'API Swagger Docs', href: 'http://localhost:8000/docs', icon: Code2, external: true },
    { name: 'Settings', to: '/settings', icon: Settings },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-xs lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 flex flex-col bg-white/95 backdrop-blur-xl border-r border-slate-200/80 transition-all duration-300 ease-in-out shadow-xs ${
          collapsed ? 'w-20' : 'w-64'
        } ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between h-18 px-4 border-b border-slate-100">
          <div className="flex items-center gap-3 overflow-hidden cursor-pointer" onClick={() => navigate('/dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 flex items-center justify-center text-white shadow-md shadow-indigo-500/25 shrink-0 ring-4 ring-indigo-50">
              <Layers className="w-5 h-5" />
            </div>
            {!collapsed && (
              <div className="flex flex-col min-w-0">
                <span className="font-extrabold text-base tracking-tight text-slate-900 leading-tight">
                  DocuQuest
                </span>
                <span className="text-[10px] font-semibold text-indigo-600 tracking-wider uppercase flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-pulse" />
                  Document AI
                </span>
              </div>
            )}
          </div>

          {/* Desktop Collapse Toggle */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex items-center justify-center w-7 h-7 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
          {/* Main Navigation */}
          <div>
            {!collapsed && (
              <p className="px-3 mb-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Workspace
              </p>
            )}
            <nav className="space-y-1">
              {mainNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.name}
                    to={item.to}
                    onClick={() => setMobileOpen(false)}
                    className={({ isActive }) =>
                      `group flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all relative ${
                        isActive
                          ? 'bg-gradient-to-r from-indigo-50 to-indigo-50/40 text-indigo-700 shadow-2xs font-bold border border-indigo-100/80'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                      } ${collapsed ? 'justify-center px-0' : ''}`
                    }
                    title={collapsed ? item.name : undefined}
                  >
                    <Icon
                      className={`w-4.5 h-4.5 shrink-0 transition-colors ${
                        collapsed ? 'mx-auto' : ''
                      }`}
                    />
                    {!collapsed && (
                      <span className="flex-1 truncate">{item.name}</span>
                    )}
                    {!collapsed && item.badge !== undefined && (
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${item.badgeColor}`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {/* Secondary Nav */}
          <div>
            {!collapsed && (
              <p className="px-3 mb-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Developer & Tools
              </p>
            )}
            <nav className="space-y-1">
              {secondaryNav.map((item) => {
                const Icon = item.icon;
                if (item.external) {
                  return (
                    <a
                      key={item.name}
                      href={item.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`group flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-all ${
                        collapsed ? 'justify-center px-0' : ''
                      }`}
                      title={collapsed ? item.name : undefined}
                    >
                      <Icon className="w-4.5 h-4.5 shrink-0" />
                      {!collapsed && <span className="flex-1 truncate">{item.name}</span>}
                    </a>
                  );
                }
                return (
                  <NavLink
                    key={item.name}
                    to={item.to!}
                    onClick={() => setMobileOpen(false)}
                    className={({ isActive }) =>
                      `group flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                        isActive
                          ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                      } ${collapsed ? 'justify-center px-0' : ''}`
                    }
                    title={collapsed ? item.name : undefined}
                  >
                    <Icon className="w-4.5 h-4.5 shrink-0" />
                    {!collapsed && <span className="flex-1 truncate">{item.name}</span>}
                  </NavLink>
                );
              })}
            </nav>
          </div>
        </div>

        {/* User Profile / Bottom section */}
        <div className="p-3 border-t border-slate-100 bg-slate-50/50">
          <div
            className={`flex items-center gap-3 p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs ${
              collapsed ? 'justify-center p-1.5' : ''
            }`}
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white font-bold flex items-center justify-center shrink-0 text-xs shadow-xs">
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-slate-900 truncate">
                  {user?.full_name || 'Administrator'}
                </p>
                <p className="text-[10px] text-slate-400 truncate">{user?.email || 'admin@docuquest.ai'}</p>
              </div>
            )}
            {!collapsed && (
              <button
                onClick={handleLogout}
                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </aside>
    </>
  );
};
