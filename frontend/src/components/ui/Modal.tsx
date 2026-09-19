import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '4xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = 'lg',
}) => {
  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '4xl': 'max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-surface-900/60 backdrop-blur-xs transition-opacity animate-fade-in"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div
        className={`relative w-full ${maxWidthClasses[maxWidth]} bg-white rounded-2xl shadow-modal border border-surface-200 overflow-hidden z-10 animate-slide-up`}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-surface-100 bg-surface-50/50">
          <div>
            <h3 className="text-lg font-bold text-surface-900 leading-snug">{title}</h3>
            {subtitle && <p className="text-xs text-surface-500 mt-1">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-surface-400 hover:text-surface-700 hover:bg-surface-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[75vh] overflow-y-auto">{children}</div>
      </div>
    </div>
  );
};
