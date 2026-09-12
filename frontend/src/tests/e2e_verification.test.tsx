import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from '../pages/LoginPage';
import { WhatIfSimulator } from '../components/WhatIfSimulator';
import { WellnessCompanion } from '../components/WellnessCompanion';
import { VoluntaryConversationCard } from '../components/VoluntaryConversationCard';
import { simulationsApi } from '../api/simulations';
import { wellnessApi } from '../api/wellness';
import { AuthProvider } from '../context/AuthContext';

// Mock specific API modules
vi.mock('../api/simulations', () => ({
  simulationsApi: {
    runSimulation: vi.fn().mockResolvedValue({
      personnel_id: 'P-000013',
      current_score: 88.1,
      current_priority: 'RED',
      projected_score: 80.3,
      projected_priority: 'RED',
      projected_delta: -7.8,
      parameter_changes: [
        { factor: 'duty_hours', before: 261.2, after: 221.2 },
        { factor: 'night_shifts', before: 14, after: 6 },
        { factor: 'recovery_leave', before: 0, after: 3 }
      ]
    })
  }
}));

vi.mock('../api/wellness', () => ({
  wellnessApi: {
    chatWithCompanion: vi.fn().mockResolvedValue({
      reply: 'Aapki baat samajh aa rahi hai. We are here to support you.',
      ai_summary: 'Personnel shared fatigue concerns.',
      extracted_signals: {
        sleep_difficulty: 'Elevated',
        fatigue: 'Elevated',
        workload_pressure: 'Moderate',
        emotional_exhaustion: 'None',
        recovery_difficulty: 'Moderate',
        personal_concern: 'None',
        morale_concern: 'None',
        social_withdrawal: false,
        positive_resilience_indicators: ['Operational dedication affirmed'],
        sentiment_valence: 'Strained',
        urgency_level: 'HIGH',
        extraction_confidence: 0.88
      },
      is_crisis: true,
      urgency_level: 'HIGH',
      confidence: 0.88,
      change_vs_previous: 'Fatigue increased compared to previous check-in.',
      welfare_signal_impact: 'Elevated Strain Signal (+5.0 pts)'
    }),
    submitCompanionSession: vi.fn().mockResolvedValue({
      id: 1,
      conversation_id: 'CONV-TEST-001',
      personnel_id: 'P-000013',
      created_at: new Date().toISOString(),
      consent_given: true,
      input_mode: 'TEXT',
      ai_summary: 'Personnel shared fatigue concerns.',
      structured_signals: {
        sleep_difficulty: 'Elevated',
        fatigue: 'Elevated',
        workload_pressure: 'Moderate',
        emotional_exhaustion: 'None',
        recovery_difficulty: 'Moderate',
        personal_concern: 'None',
        morale_concern: 'None',
        social_withdrawal: false,
        positive_resilience_indicators: ['Operational dedication affirmed'],
        sentiment_valence: 'Strained',
        urgency_level: 'HIGH',
        extraction_confidence: 0.88
      },
      confidence: 0.88,
      urgency_level: 'HIGH',
      is_crisis: true,
      status: 'PENDING_REVIEW'
    }),
    getPersonnelCompanionSignals: vi.fn().mockResolvedValue([
      {
        id: 1,
        conversation_id: 'CONV-TEST-001',
        personnel_id: 'P-000013',
        created_at: new Date().toISOString(),
        consent_given: true,
        input_mode: 'TEXT',
        ai_summary: 'Personnel voluntarily shared concerns regarding persistent fatigue and sleep disruption.',
        structured_signals: {
          sleep_difficulty: 'Elevated',
          fatigue: 'Elevated',
          workload_pressure: 'Elevated',
          emotional_exhaustion: 'Moderate',
          recovery_difficulty: 'Elevated',
          personal_concern: 'Reported (Homesickness/Family)',
          morale_concern: 'None',
          social_withdrawal: false,
          positive_resilience_indicators: ['Operational dedication affirmed'],
          sentiment_valence: 'Strained',
          urgency_level: 'MODERATE',
          extraction_confidence: 0.88
        },
        confidence: 0.88,
        urgency_level: 'MODERATE',
        is_crisis: false,
        welfare_signal_impact: 'Elevated Strain Signal (+6.5 pts)',
        change_vs_previous: 'Fatigue increased compared to previous check-in.',
        status: 'PENDING_REVIEW'
      }
    ]),
    reviewCompanionConversation: vi.fn().mockResolvedValue({
      id: 1,
      conversation_id: 'CONV-TEST-001',
      personnel_id: 'P-000013',
      created_at: new Date().toISOString(),
      consent_given: true,
      input_mode: 'TEXT',
      ai_summary: 'Personnel voluntarily shared concerns.',
      structured_signals: {
        sleep_difficulty: 'Elevated',
        fatigue: 'Elevated',
        workload_pressure: 'Elevated',
        emotional_exhaustion: 'Moderate',
        recovery_difficulty: 'Elevated',
        personal_concern: 'None',
        morale_concern: 'None',
        social_withdrawal: false,
        positive_resilience_indicators: [],
        sentiment_valence: 'Strained',
        urgency_level: 'MODERATE',
        extraction_confidence: 0.88
      },
      confidence: 0.88,
      urgency_level: 'MODERATE',
      is_crisis: false,
      status: 'ACKNOWLEDGED',
      welfare_officer_notes: 'Reviewed and scheduled supportive check-in.'
    })
  }
}));

describe('SAATHI End-to-End Visual & Functional Verification', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('Checklist 1 & 2: Login Page displays institutional theme and evaluator role switchers', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </BrowserRouter>
    );

    // Branding & Institutional elements
    expect(screen.getByText('SAATHI')).toBeInTheDocument();
    expect(screen.getByText(/AI-Based Personnel Welfare Support & Monitoring Decision System/i)).toBeInTheDocument();
    expect(screen.getByText(/भारत सरकार/i)).toBeInTheDocument();
    expect(screen.getByText('Welfare Officer')).toBeInTheDocument();
    expect(screen.getByText('Commander')).toBeInTheDocument();
    expect(screen.getByText(/P-000013/i)).toBeInTheDocument();
    expect(screen.getByText('Analyst')).toBeInTheDocument();
    expect(screen.getByText('Admin / Audit')).toBeInTheDocument();

    // Click quick login fills credentials
    fireEvent.click(screen.getByText('Welfare Officer'));
    const usernameInput = screen.getByLabelText(/Username \/ Service ID/i) as HTMLInputElement;
    expect(usernameInput.value).toBe('welfare_officer');
  });

  it('Checklist 5, 6 & 7: What-If Simulator executes model-based scenario projection (88.1 -> 80.3)', async () => {
    render(
      <WhatIfSimulator
        personnelId="P-000013"
        currentScore={88.1}
        currentPriority="RED"
      />
    );

    expect(screen.getByText(/What-If Welfare Simulator/i)).toBeInTheDocument();
    expect(screen.getByText(/SCENARIO SIMULATION/i)).toBeInTheDocument();

    // Click simulation button
    const simulateBtn = screen.getByRole('button', { name: /Simulate Operational Impact/i });
    fireEvent.click(simulateBtn);

    await waitFor(() => {
      expect(simulationsApi.runSimulation).toHaveBeenCalledWith('P-000013', {
        reduce_night_shifts: 8,
        reduce_duty_hours: 40,
        grant_recovery_days: 3,
        reduce_overtime_hours: 10
      });
      expect(screen.getByText('80.3')).toBeInTheDocument();
      expect(screen.getByText(/-7.8 pts/i)).toBeInTheDocument();
    });
  });

  it('Checklist 8: Voluntary Conversation Card renders structured signals and non-clinical interpretation', async () => {
    render(<VoluntaryConversationCard personnelId="P-000013" />);

    await waitFor(() => {
      expect(screen.getByText('Voluntary Wellness Conversation')).toBeInTheDocument();
    });

    expect(screen.getByText(/AI Non-Clinical Interpretation/i)).toBeInTheDocument();
    expect(screen.getByText('Self-Reported Fatigue')).toBeInTheDocument();
    expect(screen.getByText('Sleep Difficulty')).toBeInTheDocument();
    expect(screen.getByText('Acknowledge & Save Notes')).toBeInTheDocument();
  });

  it('Checklist 8 & 9: Wellness Companion renders privacy safeguards, handles message and reveals crisis safety banner', async () => {
    render(<WellnessCompanion personnelId="P-000013" />);

    expect(screen.getByText('SAATHI Wellness Companion')).toBeInTheDocument();
    expect(screen.getByText(/A private, voluntary space to share how you're doing/i)).toBeInTheDocument();
    expect(screen.getByText('Voluntary & Protected')).toBeInTheDocument();

    // Send a message
    const input = screen.getByPlaceholderText(/Share how you are feeling/i);
    fireEvent.change(input, { target: { value: 'I feel exhausted from night shifts' } });
    const sendBtn = screen.getByTitle('Send Message');
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(wellnessApi.chatWithCompanion).toHaveBeenCalled();
      // Should show crisis safety hotline banner
      expect(screen.getByText(/1800-599-0019/i)).toBeInTheDocument();
      expect(screen.getByText(/Immediate Human Care & Support Assistance/i)).toBeInTheDocument();
    });
  });
});
