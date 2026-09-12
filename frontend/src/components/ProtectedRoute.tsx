import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';

interface ProtectedRouteProps {
  allowedRoles?: UserRole[];
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles, children }) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs text-slate-400">Authenticating SAATHI session...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to the default dashboard appropriate for their role
    if (user.role === 'COMMANDER') return <Navigate to="/commander" replace />;
    if (user.role === 'ANALYST') return <Navigate to="/analyst" replace />;
    if (user.role === 'PERSONNEL') return <Navigate to="/portal" replace />;
    if (user.role === 'ADMIN') return <Navigate to="/welfare" replace />;
    return <Navigate to="/welfare" replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};
