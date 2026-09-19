import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { Modal } from '../ui/Modal';
import { UploadDropzone } from '../documents/UploadDropzone';

export const AppShell: React.FC = () => {
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface-50 flex">
      {/* Sidebar */}
      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          collapsed ? 'lg:pl-20' : 'lg:pl-64'
        }`}
      >
        <Topbar
          onOpenMobileNav={() => setMobileOpen(true)}
          onOpenUploadModal={() => setIsUploadModalOpen(true)}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>

      {/* Global Upload Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Examination Document"
        subtitle="Add a new PDF or image question paper for instant OCR extraction"
      >
        <UploadDropzone
          onSuccess={(docId) => {
            setIsUploadModalOpen(false);
            navigate(`/documents/${docId}`);
          }}
        />
      </Modal>
    </div>
  );
};
