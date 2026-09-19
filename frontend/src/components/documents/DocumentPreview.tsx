import React, { useState } from 'react';
import { Document, DocumentPage } from '../../types';
import {
  FileText,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Sparkles,
  Layers,
  Eye,
} from 'lucide-react';

interface DocumentPreviewProps {
  document: Document;
  pages?: DocumentPage[];
  activePageNumber?: number;
  highlightedQuestionText?: string;
  className?: string;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  document,
  pages = [],
  activePageNumber = 1,
  highlightedQuestionText,
  className = '',
}) => {
  const [currentPage, setCurrentPage] = useState<number>(activePageNumber);
  const [zoomLevel, setZoomLevel] = useState<number>(100);

  const totalPages = document.total_pages || (pages.length > 0 ? pages.length : 1);

  const handleNext = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };

  const handlePrev = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  const currentPageData = pages.find((p) => p.page_number === currentPage);

  return (
    <div className={`card-panel flex flex-col bg-surface-900 text-white rounded-2xl overflow-hidden shadow-card ${className}`}>
      {/* Viewer Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-surface-950 border-b border-surface-800 text-xs">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-brand-400" />
          <span className="font-semibold text-surface-200 truncate max-w-[180px]">
            {document.original_filename}
          </span>
          {currentPageData?.ocr_applied && (
            <span className="px-1.5 py-0.5 rounded bg-brand-900/60 text-brand-300 border border-brand-700/60 text-[10px] font-medium">
              OCR Processed
            </span>
          )}
        </div>

        {/* Page navigation & Zoom controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-surface-800/80 rounded-lg px-2 py-1 border border-surface-700/60">
            <button
              onClick={handlePrev}
              disabled={currentPage <= 1}
              className="p-0.5 rounded hover:bg-surface-700 disabled:opacity-40"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="text-[11px] font-mono px-1">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={handleNext}
              disabled={currentPage >= totalPages}
              className="p-0.5 rounded hover:bg-surface-700 disabled:opacity-40"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="hidden sm:flex items-center gap-1 bg-surface-800/80 rounded-lg px-2 py-1 border border-surface-700/60 text-[11px]">
            <button
              onClick={() => setZoomLevel(Math.max(75, zoomLevel - 15))}
              className="p-0.5 rounded hover:bg-surface-700"
            >
              <ZoomOut className="w-3 h-3" />
            </button>
            <span className="w-8 text-center">{zoomLevel}%</span>
            <button
              onClick={() => setZoomLevel(Math.min(150, zoomLevel + 15))}
              className="p-0.5 rounded hover:bg-surface-700"
            >
              <ZoomIn className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Viewer Canvas */}
      <div className="flex-1 p-6 flex items-center justify-center overflow-auto bg-surface-900/90 min-h-[380px]">
        <div
          className="relative bg-white text-surface-900 rounded-xl shadow-2xl p-8 max-w-xl w-full border border-surface-300 transition-all duration-200"
          style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center' }}
        >
          {/* Mock Document Page Layout */}
          <div className="border-b border-surface-200 pb-3 mb-4 flex justify-between items-center text-[10px] text-surface-400 font-mono">
            <span>{document.title || 'EXAMINATION PAPER'}</span>
            <span>PAGE {currentPage} OF {totalPages}</span>
          </div>

          {highlightedQuestionText ? (
            <div className="space-y-4">
              <div className="p-3 bg-brand-50/80 border-2 border-brand-400 rounded-lg text-xs leading-relaxed text-surface-900 relative">
                <span className="absolute -top-2.5 right-2 px-1.5 py-0.2 bg-brand-600 text-white rounded text-[9px] font-bold uppercase tracking-wider">
                  Source Region
                </span>
                <p className="font-semibold text-brand-900 mb-1">Selected Question Content:</p>
                <p className="whitespace-pre-wrap">{highlightedQuestionText}</p>
              </div>

              {/* Surrounding mock text lines */}
              <div className="space-y-2 opacity-30 select-none">
                <div className="h-3 bg-surface-400 rounded w-5/6" />
                <div className="h-3 bg-surface-400 rounded w-full" />
                <div className="h-3 bg-surface-400 rounded w-4/6" />
              </div>
            </div>
          ) : (
            <div className="space-y-4 text-xs text-surface-700 leading-relaxed">
              <div className="text-center font-bold text-sm text-surface-900 border-b border-surface-200 pb-2 mb-4">
                {document.original_filename.toUpperCase().replace(/\.[^/.]+$/, '')}
              </div>

              <div className="p-3 bg-surface-50 border border-surface-200 rounded-lg text-[11px] text-surface-500">
                <p className="font-medium text-surface-700">Document Source Information:</p>
                <p className="mt-0.5">MIME Type: {document.content_type} &bull; File Size: {(document.file_size_bytes / 1024).toFixed(1)} KB</p>
                <p className="mt-0.5">Extraction Status: {document.status}</p>
              </div>

              {/* Representative document lines */}
              <div className="space-y-2.5 pt-2">
                <div className="h-3.5 bg-surface-200 rounded w-11/12" />
                <div className="h-3.5 bg-surface-200 rounded w-full" />
                <div className="h-3.5 bg-surface-200 rounded w-4/5" />
                <div className="h-3.5 bg-surface-200 rounded w-full" />
                <div className="h-3.5 bg-surface-200 rounded w-3/4" />
              </div>

              <div className="mt-6 pt-4 border-t border-surface-200 flex items-center justify-between text-[11px] text-surface-400">
                <span>DocuQuest Optical Layout Engine</span>
                <span className="flex items-center gap-1 text-brand-600 font-medium">
                  <Sparkles className="w-3 h-3" />
                  Verified
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
