import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { CommanderDashboardPage } from '../pages/CommanderDashboardPage';
import { AuthProvider } from '../context/AuthContext';

// Mock APIs
vi.mock('../api/analytics', () => ({
  analyticsApi: {
    getCommanderOverview: vi.fn().mockResolvedValue({
      total_strength: 1470,
      high_risk_total: 143,
      interventions_active_count: 12,
      interventions_improved_count: 8,
      priority_distribution: [
        { priority: 'GREEN', count: 1050, percentage: 71.4 },
        { priority: 'YELLOW', count: 277, percentage: 18.8 },
        { priority: 'ORANGE', count: 110, percentage: 7.5 },
        { priority: 'RED', count: 33, percentage: 2.3 }
      ],
      department_breakdown: [
        {
          department: 'Operations',
          total_personnel: 500,
          green_count: 350,
          yellow_count: 100,
          orange_count: 40,
          red_count: 10,
          avg_support_score: 34.5
        }
      ]
    })
  }
}));

vi.mock('../api/commander', () => ({
  commanderApi: {
    getPendingCheckIns: vi.fn().mockResolvedValue({
      total_pending: 1,
      total_overdue: 1,
      total_followup_requested: 0,
      current_checkin_cycle: 'September 2026',
      items: [
        {
          personnel_id: 'P-000042',
          display_name: 'Field Constable',
          unit: 'Operations',
          role: 'Constable',
          last_checkin_date: '2026-08-05',
          expected_checkin_month: 'September 2026',
          days_overdue: 11,
          submission_status: 'NOT_SUBMITTED',
          follow_up_status: 'NONE',
          last_followup_at: null,
          last_followup_by: null
        }
      ]
    }),
    requestFollowUp: vi.fn().mockResolvedValue({
      status: 'SUCCESS',
      message: 'Follow-up registered',
      followup_id: 101,
      personnel_id: 'P-000042',
      target_month: '2026-09',
      requested_at: new Date().toISOString(),
      follow_up_status: 'FOLLOW_UP_REQUESTED'
    })
  }
}));

describe('Commander Monthly Check-In Follow-Up UI', () => {
  it('renders Monthly Check-In Follow-up section and pending personnel data', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <CommanderDashboardPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Monthly Check-In Follow-up/i)).toBeInTheDocument();
      expect(screen.getByText('P-000042')).toBeInTheDocument();
      expect(screen.getByText('11 days')).toBeInTheDocument();
      expect(screen.getByText(/Request Check-In/i)).toBeInTheDocument();
    });
  });

  it('strictly isolates private wellness scores from commander table', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <CommanderDashboardPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('P-000042')).toBeInTheDocument();
    });

    // Verify forbidden individual terms are not rendered in the checkin follow-up table
    expect(screen.queryByText(/Support Score: P-000042/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Individual SHAP/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Survey Answers/i)).not.toBeInTheDocument();
  });
});
