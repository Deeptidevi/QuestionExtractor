import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import { AppShell } from './components/layout/AppShell';

import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { DocumentDetailsPage } from './pages/DocumentDetailsPage';
import { QuestionsPage } from './pages/QuestionsPage';
import { QuestionDetailsPage } from './pages/QuestionDetailsPage';
import { ReviewQueuePage } from './pages/ReviewQueuePage';
import { AnswerKeysPage } from './pages/AnswerKeysPage';
import { RelationshipsPage } from './pages/RelationshipsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 30, // 30s
    },
  },
});

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <AuthProvider>
            <BrowserRouter>
              <Routes>
                {/* Main App Layout */}
                <Route element={<AppShell />}>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/documents" element={<DocumentsPage />} />
                  <Route path="/documents/:id" element={<DocumentDetailsPage />} />
                  <Route path="/questions" element={<QuestionsPage />} />
                  <Route path="/questions/:id" element={<QuestionDetailsPage />} />
                  <Route path="/review" element={<ReviewQueuePage />} />
                  <Route path="/answer-keys" element={<AnswerKeysPage />} />
                  <Route path="/relationships" element={<RelationshipsPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Route>

                {/* Optional direct auth routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Fallback directly to Dashboard */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </BrowserRouter>
          </AuthProvider>
        </ToastProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
