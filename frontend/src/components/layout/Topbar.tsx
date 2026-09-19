import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Menu,
  Search,
  Bell,
  UploadCloud,
  Command,
  ChevronRight,
  Sparkles,
  Zap,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface TopbarProps {
  onOpenMobileNav: () => void;
  onOpenUploadModal: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  onOpenMobileNav,
  onOpenUploadModal,
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');

  const getPageInfo = () => {
    const path = location.pathname;
    if (path === '/dashboard') return { title: 'Dashboard', category: 'Overview' };
    if (path.startsWith('/documents')) return { title: 'Documents Management', category: 'Library' };
    if (path.startsWith('/questions')) return { title: 'Question Explorer', category: 'Content' };
    if (path.startsWith('/review')) return { title: 'Human Review Queue', category: 'Quality' };
    if (path.startsWith('/answer-keys')) return { title: 'Answer Keys & Matching', category: 'Quality' };
    if (path.startsWith('/relationships')) return { title: 'Document Relationships', category: 'Graph' };
    if (path.startsWith('/analytics')) return { title: 'Analytics & Insights', category: 'Performance' };
    if (path.startsWith('/settings')) return { title: 'System Settings', category: 'Configuration' };
    return { title: 'DocuQuest', category: 'Overview' };
  };

  const pageInfo = getPageInfo();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/questions?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-18 px-4 sm:px-8 bg-white/80 backdrop-blur-xl border-b border-slate-200/80 shadow-2xs">
      {/* Left: Mobile Menu & Breadcrumbs */}
      <div className="flex items-center gap-4">
        <button
          onClick={onOpenMobileNav}
          className="p-2 -ml-2 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-100 lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-xs">
          <span className="font-semibold text-slate-400 hidden sm:inline">{pageInfo.category}</span>
          <ChevronRight className="w-3.5 h-3.5 text-slate-300 hidden sm:inline" />
          <h1 className="text-base sm:text-lg font-extrabold text-slate-900 tracking-tight">
            {pageInfo.title}
          </h1>
        </div>
      </div>

      {/* Center: Global Search */}
      <div className="hidden md:flex flex-1 max-w-md mx-6">
        <form onSubmit={handleSearchSubmit} className="relative w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents, questions, stems..."
            className="w-full pl-10 pr-12 py-2 text-xs sm:text-sm bg-slate-50/80 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-slate-800 placeholder-slate-400 shadow-2xs"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-slate-200/60 text-[10px] text-slate-500 font-mono font-medium">
            <Command className="w-3 h-3" />
            <span>K</span>
          </div>
        </form>
      </div>

      {/* Right: Actions & Profile */}
      <div className="flex items-center gap-3.5">
        {/* Quick Upload CTA */}
        <button
          onClick={onOpenUploadModal}
          className="btn-primary py-2 px-4 text-xs sm:text-sm"
        >
          <UploadCloud className="w-4 h-4" />
          <span className="hidden sm:inline">+ Upload Document</span>
        </button>

        {/* Notifications */}
        <button
          className="relative p-2 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          title="Notifications"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-600 rounded-full ring-2 ring-white" />
        </button>

        <div className="h-6 w-px bg-slate-200 hidden sm:block" />

        {/* User Info */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-sky-500 text-white font-bold flex items-center justify-center text-xs shadow-xs ring-2 ring-indigo-50">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'A'}
          </div>
        </div>
      </div>
    </header>
  );
};
