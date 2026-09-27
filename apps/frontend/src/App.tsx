import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';

import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ReportDamagePage } from './pages/ReportDamagePage';
import { AssessmentResultPage } from './pages/AssessmentResultPage';
import { DashboardPage } from './pages/DashboardPage';
import { AssessmentDetailsPage } from './pages/AssessmentDetailsPage';
import { AskRoadSensePage } from './pages/AskRoadSensePage';
import { ProfilePage } from './pages/ProfilePage';
import { DemoAdminDashboardPage } from './pages/DemoAdminDashboardPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-slate-50 font-sans text-slate-900 antialiased selection:bg-blue-100 selection:text-blue-900">
          <Navbar />
          <main className="flex-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/demo-dashboard" element={<DemoAdminDashboardPage />} />

              {/* Protected Routes */}
              <Route
                path="/report"
                element={
                  <ProtectedRoute>
                    <ReportDamagePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/assessment-result"
                element={
                  <ProtectedRoute>
                    <AssessmentResultPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/assessment/:id"
                element={
                  <ProtectedRoute>
                    <AssessmentDetailsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/ask"
                element={
                  <ProtectedRoute>
                    <AskRoadSensePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
