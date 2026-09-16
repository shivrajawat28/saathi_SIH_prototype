import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from '../pages/LoginPage';
import { AuthProvider } from '../context/AuthContext';

vi.mock('../api/auth');

describe('Frontend Authentication Flow', () => {
  it('renders login form and quick demo role switchers', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('SAATHI')).toBeInTheDocument();
    expect(screen.getByLabelText(/Username \/ Service ID/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByText('Welfare Officer')).toBeInTheDocument();
    expect(screen.getByText('Commander')).toBeInTheDocument();
    expect(screen.getByText(/P-000013/i)).toBeInTheDocument();
    expect(screen.getByText(/P-000001/i)).toBeInTheDocument();
    expect(screen.getByText('Analyst')).toBeInTheDocument();
    expect(screen.getByText('Admin / Audit')).toBeInTheDocument();
  });

  it('clicking quick demo button auto-fills credentials', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </BrowserRouter>
    );

    const commanderButton = screen.getByText('Commander');
    fireEvent.click(commanderButton);

    const usernameInput = screen.getByLabelText(/Username \/ Service ID/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/Password/i) as HTMLInputElement;

    expect(usernameInput.value).toBe('commander');
    expect(passwordInput.value).toBe('commander123');
  });

  it('displays ethical notice on login screen', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText(/AI-Based Personnel Welfare Support & Monitoring Decision System/i)).toBeInTheDocument();
    expect(screen.getByText(/Decision Support Aid. AI suggests; authorized humans decide/i)).toBeInTheDocument();
  });

  it('correctly distinguishes 401 vs network/server wake-up errors', async () => {
    const { getApiErrorMessage } = await import('../api/client');

    // 401 Unauthorized
    const err401 = { response: { status: 401 } };
    expect(getApiErrorMessage(err401)).toBe('Invalid username or password.');

    // 502 Bad Gateway (Server Waking Up on Render)
    const err502 = { response: { status: 502 } };
    expect(getApiErrorMessage(err502)).toBe('SAATHI service is temporarily unavailable (waking up). Please try again.');

    // 503 Service Unavailable
    const err503 = { response: { status: 503 } };
    expect(getApiErrorMessage(err503)).toBe('SAATHI service is temporarily unavailable (waking up). Please try again.');

    // Timeout Error
    const errTimeout = { code: 'ECONNABORTED', message: 'timeout of 60000ms exceeded' };
    expect(getApiErrorMessage(errTimeout)).toBe('The service is waking up. Please retry in a moment.');

    // Network Disconnect
    const errNetwork = { code: 'ERR_NETWORK', message: 'Network Error' };
    expect(getApiErrorMessage(errNetwork)).toBe('Unable to reach the SAATHI service. Please check your connection.');
  });
});
