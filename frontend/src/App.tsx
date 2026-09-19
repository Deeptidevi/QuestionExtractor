import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppShell } from './components/layout/AppShell';

import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
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
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Auth Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Protected App Routes */}
              <Route element={<ProtectedRoute />}>
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
              </Route>

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </QueryClientProvider>
  );
};

export default App;
