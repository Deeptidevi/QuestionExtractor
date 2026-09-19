import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  X,
  Loader2,
  Sparkles,
  Zap,
  FileCheck,
  FolderOpen,
} from 'lucide-react';
import { documentsApi } from '../../api/documents';
import { useToast } from '../../context/ToastContext';

interface UploadDropzoneProps {
  onSuccess?: (docId: string) => void;
  compact?: boolean;
}

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({
  onSuccess,
  compact = false,
}) => {
  const { success, error } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [customTitle, setCustomTitle] = useState('');
  const [syncProcess, setSyncProcess] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const MAX_SIZE_MB = 50;
  const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];

  const validateAndSetFile = (file: File) => {
    // 1. Check size
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      error('File too large', `File size exceeds the maximum limit of ${MAX_SIZE_MB}MB.`);
      return;
    }

    // 2. Check extension & MIME
    const isValidType = ALLOWED_TYPES.includes(file.type) ||
      /\.(pdf|jpe?g|png)$/i.test(file.name);

    if (!isValidType) {
      error('Unsupported format', 'Please upload a valid PDF, JPG, JPEG, or PNG document.');
      return;
    }

    setSelectedFile(file);
    if (!customTitle) {
      setCustomTitle(file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' '));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(25);

    try {
      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(interval);
            return prev;
          }
          return prev + 20;
        });
      }, 120);

      const res = await documentsApi.uploadDocument({
        file: selectedFile,
        title: customTitle || undefined,
        sync_process: syncProcess,
      });

      clearInterval(interval);
      setUploadProgress(100);

      success(
        'Processing Succeeded',
        syncProcess
          ? 'Document analyzed instantly! All questions and answer keys extracted.'
          : 'Document uploaded and queued for processing pipeline.'
      );

      setSelectedFile(null);
      setCustomTitle('');
      if (fileInputRef.current) fileInputRef.current.value = '';

      if (onSuccess) {
        onSuccess(res.document_id);
      }
    } catch (err: any) {
      console.error('Upload failed:', err);
      const msg = err.response?.data?.error?.message || 'Failed to upload document. Please try again.';
      error('Upload Failed', msg);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="w-full">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
        className="hidden"
      />

      {!selectedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`group relative flex flex-col items-center justify-center p-8 sm:p-12 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-300 ${
            isDragging
              ? 'border-indigo-500 bg-indigo-50/70 scale-[1.01] shadow-glow ring-4 ring-indigo-100'
              : 'border-slate-300 hover:border-indigo-400 bg-gradient-to-b from-white to-slate-50/60 hover:bg-indigo-50/20 shadow-sm'
          } ${compact ? 'p-6' : ''}`}
        >
          {/* Glowing Icon Container */}
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 group-hover:scale-110 group-hover:shadow-indigo-500/50 transition-all duration-300 mb-4 ring-8 ring-indigo-50">
            <UploadCloud className="w-8 h-8" />
          </div>

          <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-1.5 text-center">
            Drop your question paper here, or <span className="text-indigo-600 underline decoration-indigo-300 underline-offset-4">browse files</span>
          </h3>
          <p className="text-xs text-slate-500 mb-5 max-w-md text-center leading-relaxed">
            Drag in your multi-page PDF examination papers, scanned question sheets (PNG/JPG), or answer keys up to 50 MB.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-2">
            <span className="px-2.5 py-1 rounded-lg bg-white text-xs font-bold text-slate-700 border border-slate-200 shadow-2xs">
              PDF
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-white text-xs font-bold text-slate-700 border border-slate-200 shadow-2xs">
              JPG / JPEG
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-white text-xs font-bold text-slate-700 border border-slate-200 shadow-2xs">
              PNG
            </span>
            <span className="text-xs font-semibold text-indigo-600 flex items-center gap-1 pl-1">
              <Sparkles className="w-3.5 h-3.5" />
              Auto-OCR & Layout AI
            </span>
          </div>
        </div>
      ) : (
        <div className="card-panel p-6 bg-white border-indigo-200 shadow-md animate-slide-up">
          {/* Selected File Summary */}
          <div className="flex items-start justify-between gap-4 pb-5 border-b border-slate-100">
            <div className="flex items-center gap-3.5 min-w-0">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white flex items-center justify-center shrink-0 shadow-sm ring-4 ring-indigo-50">
                {selectedFile.type?.includes('pdf') || selectedFile.name?.toLowerCase().endsWith('.pdf') ? (
                  <FileText className="w-6 h-6" />
                ) : (
                  <ImageIcon className="w-6 h-6" />
                )}
              </div>
              <div className="min-w-0">
                <h4 className="text-sm font-bold text-slate-900 truncate">
                  {selectedFile.name}
                </h4>
                <p className="text-xs text-slate-400 mt-0.5 font-medium">
                  {formatFileSize(selectedFile.size)} &bull; {selectedFile.type || 'Document'}
                </p>
              </div>
            </div>

            {!isUploading && (
              <button
                onClick={() => setSelectedFile(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                title="Remove file"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Configuration Form */}
          <div className="mt-5 space-y-4">
            <div>
              <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Document Title (Optional)
              </label>
              <input
                type="text"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                placeholder="e.g. Computer Science Midterm Examination 2024"
                disabled={isUploading}
                className="w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all disabled:opacity-60 font-medium"
              />
            </div>

            {/* Instant Mode Toggle */}
            <div className="flex items-center justify-between p-3.5 rounded-xl bg-gradient-to-r from-indigo-50/80 to-sky-50/50 border border-indigo-100">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-lg bg-indigo-600 text-white shadow-xs">
                  <Zap className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900">Instant Real-time Extraction</p>
                  <p className="text-[11px] text-slate-500">Synchronously parse OCR, segment questions, and score confidence immediately</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={syncProcess}
                  onChange={(e) => setSyncProcess(e.target.checked)}
                  disabled={isUploading}
                  className="sr-only peer"
                />
                <div className="w-10 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>

            {/* Upload & Processing Progress */}
            {isUploading && (
              <div className="space-y-2 pt-2">
                <div className="flex justify-between text-xs font-semibold text-slate-700">
                  <span className="flex items-center gap-2 text-indigo-600">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Extracting questions, options & answer keys...
                  </span>
                  <span className="font-mono text-indigo-700">{uploadProgress}%</span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden p-0.5 border border-slate-200">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-600 to-sky-500 rounded-full transition-all duration-300 shadow-sm"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-3">
              <button
                type="button"
                onClick={() => setSelectedFile(null)}
                disabled={isUploading}
                className="btn-secondary text-xs sm:text-sm"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleUpload}
                disabled={isUploading}
                className="btn-primary text-xs sm:text-sm py-2.5 px-5"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Processing Pipeline...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Start AI Extraction
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
