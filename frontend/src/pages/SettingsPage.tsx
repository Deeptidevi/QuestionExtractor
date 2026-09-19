import React from 'react';
import { useAuth } from '../context/AuthContext';
import {
  User,
  Shield,
  Sliders,
  Cpu,
  FileCheck,
  Bell,
  HardDrive,
  CheckCircle2,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl pb-16">
      {/* Header */}
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-surface-900 tracking-tight">System Settings</h2>
        <p className="text-xs sm:text-sm text-surface-500 mt-1">
          Manage your profile, extraction parameters, OCR engine preferences, and security limits.
        </p>
      </div>

      {/* Section 1: User Profile */}
      <div className="card-panel p-6 bg-white space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-surface-100">
          <User className="w-5 h-5 text-brand-600" />
          <h3 className="text-sm font-bold text-surface-900">User Profile</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-surface-500 font-medium mb-1">Full Name</label>
            <p className="font-semibold text-surface-900 bg-surface-50 p-2.5 rounded-xl border border-surface-200">
              {user?.full_name || 'Administrator'}
            </p>
          </div>
          <div>
            <label className="block text-surface-500 font-medium mb-1">Email Address</label>
            <p className="font-semibold text-surface-900 bg-surface-50 p-2.5 rounded-xl border border-surface-200">
              {user?.email || 'admin@docuquest.ai'}
            </p>
          </div>
        </div>
      </div>

      {/* Section 2: Pipeline Confidence Thresholds */}
      <div className="card-panel p-6 bg-white space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-surface-100">
          <Sliders className="w-5 h-5 text-brand-600" />
          <h3 className="text-sm font-bold text-surface-900">Extraction & Confidence Thresholds</h3>
        </div>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded-xl bg-surface-50 border border-surface-200">
            <div>
              <p className="font-bold text-surface-900">Auto-Approval Threshold</p>
              <p className="text-[11px] text-surface-500">Questions scoring above this are marked verified</p>
            </div>
            <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-lg font-bold">
              0.85 (85%)
            </span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-surface-50 border border-surface-200">
            <div>
              <p className="font-bold text-surface-900">Human Review Threshold</p>
              <p className="text-[11px] text-surface-500">Questions scoring below this enter review queue</p>
            </div>
            <span className="px-3 py-1 bg-amber-100 text-amber-800 rounded-lg font-bold">
              0.60 (60%)
            </span>
          </div>
        </div>
      </div>

      {/* Section 3: Engine & File Limits */}
      <div className="card-panel p-6 bg-white space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-surface-100">
          <Cpu className="w-5 h-5 text-brand-600" />
          <h3 className="text-sm font-bold text-surface-900">OCR & Document Storage</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-surface-50 border border-surface-200">
            <span className="text-[11px] text-surface-500 font-medium block">Max File Size</span>
            <span className="text-sm font-bold text-surface-900 mt-1 block">50 MB</span>
          </div>
          <div className="p-3.5 rounded-xl bg-surface-50 border border-surface-200">
            <span className="text-[11px] text-surface-500 font-medium block">OCR Provider</span>
            <span className="text-sm font-bold text-surface-900 mt-1 block">Tesseract / PyPDF</span>
          </div>
          <div className="p-3.5 rounded-xl bg-surface-50 border border-surface-200">
            <span className="text-[11px] text-surface-500 font-medium block">Storage Backend</span>
            <span className="text-sm font-bold text-surface-900 mt-1 block">Local / SHA-256</span>
          </div>
        </div>
      </div>
    </div>
  );
};
