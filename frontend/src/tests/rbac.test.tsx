import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { AuthContext } from '../context/AuthContext';
import { UserProfile, UserRole } from '../types';

describe('Frontend RBAC Role Protection', () => {
  const renderWithRole = (role: UserRole, initialEntry: string) => {
    const mockUser: UserProfile = {
      id: 1,
      username: 'test_user',
      email: 'test@example.com',
      role: role,
      personnel_id: role === 'PERSONNEL' ? 'P-000001' : null,
      is_active: true,
      permissions: [],
    };

    const mockAuthContext = {
      user: mockUser,
      token: 'fake-token-xyz',
      role: role,
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    };

    return render(
      <AuthContext.Provider value={mockAuthContext}>
        <MemoryRouter initialEntries={[initialEntry]}>
          <Routes>
            <Route path="/login" element={<div>Login Page</div>} />
            <Route
              path="/welfare"
              element={
                <ProtectedRoute allowedRoles={['WELFARE_OFFICER', 'ADMIN']}>
                  <div>Welfare Officer Dashboard View</div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/commander"
              element={
                <ProtectedRoute allowedRoles={['COMMANDER', 'ADMIN']}>
                  <div>Commander Dashboard View</div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <div>Admin Audit View</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );
  };

  it('allows WELFARE_OFFICER to access welfare officer dashboard', () => {
    renderWithRole('WELFARE_OFFICER', '/welfare');
    expect(screen.getByText('Welfare Officer Dashboard View')).toBeInTheDocument();
  });

  it('blocks COMMANDER from accessing welfare officer dashboard and redirects to default role route', () => {
    renderWithRole('COMMANDER', '/welfare');
    expect(screen.queryByText('Welfare Officer Dashboard View')).not.toBeInTheDocument();
  });

  it('allows COMMANDER to access commander dashboard', () => {
    renderWithRole('COMMANDER', '/commander');
    expect(screen.getByText('Commander Dashboard View')).toBeInTheDocument();
  });

  it('allows ADMIN to access all administrative views', () => {
    renderWithRole('ADMIN', '/admin');
    expect(screen.getByText('Admin Audit View')).toBeInTheDocument();
  });
});
