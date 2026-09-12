import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';

import { LoginPage } from './pages/LoginPage';
import { WelfareDashboardPage } from './pages/WelfareDashboardPage';
import { PersonnelDetailPage } from './pages/PersonnelDetailPage';
import { CommanderDashboardPage } from './pages/CommanderDashboardPage';
import { AnalystDashboardPage } from './pages/AnalystDashboardPage';
import { PersonnelPortalPage } from './pages/PersonnelPortalPage';
import { AdminAuditPage } from './pages/AdminAuditPage';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-2 sm:p-4 md:p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Login Route */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            
            {/* Welfare Officer & Admin */}
            <Route
              path="/welfare"
              element={
                <Layout>
                  <WelfareDashboardPage />
                </Layout>
              }
            />

            {/* Personnel Detail View */}
            <Route
              path="/personnel/:id"
              element={
                <Layout>
                  <PersonnelDetailPage />
                </Layout>
              }
            />

            {/* Commander Dashboard */}
            <Route
              path="/commander"
              element={
                <Layout>
                  <CommanderDashboardPage />
                </Layout>
              }
            />

            {/* Analyst Dashboard */}
            <Route
              path="/analyst"
              element={
                <Layout>
                  <AnalystDashboardPage />
                </Layout>
              }
            />

            {/* Personnel Self-Service Portal */}
            <Route
              path="/portal"
              element={
                <Layout>
                  <PersonnelPortalPage />
                </Layout>
              }
            />

            {/* Admin Audit & User Management */}
            <Route
              path="/audit"
              element={
                <Layout>
                  <AdminAuditPage />
                </Layout>
              }
            />

            {/* Default Catch-all */}
            <Route path="*" element={<Navigate to="/welfare" replace />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
