import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { WellnessCompanion } from '../components/WellnessCompanion';
import { VoluntaryConversationCard } from '../components/VoluntaryConversationCard';
import { wellnessApi } from '../api/wellness';

// Mock wellness API
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
        urgency_level: 'MODERATE',
        extraction_confidence: 0.88
      },
      is_crisis: false,
      urgency_level: 'MODERATE',
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
        urgency_level: 'MODERATE',
        extraction_confidence: 0.88
      },
      confidence: 0.88,
      urgency_level: 'MODERATE',
      is_crisis: false,
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

describe('SAATHI Voluntary AI Wellness Companion Frontend', () => {
  it('renders WellnessCompanion with non-diagnostic voluntary interface', () => {
    render(<WellnessCompanion personnelId="P-000013" />);

    expect(screen.getByText('SAATHI Wellness Companion')).toBeInTheDocument();
    expect(screen.getByText('Voluntary AI Welfare Companion')).toBeInTheDocument();
    expect(screen.getByText(/A private, voluntary space to share how you're doing/i)).toBeInTheDocument();
    expect(screen.getByText('Voluntary & Protected')).toBeInTheDocument();
  });

  it('renders VoluntaryConversationCard for Welfare Officer drilldown', async () => {
    render(<VoluntaryConversationCard personnelId="P-000013" />);

    await waitFor(() => {
      expect(screen.getByText('Voluntary Wellness Conversation')).toBeInTheDocument();
    });

    expect(screen.getByText(/AI Non-Clinical Interpretation/i)).toBeInTheDocument();
    expect(screen.getByText('Self-Reported Fatigue')).toBeInTheDocument();
    expect(screen.getByText('Sleep Difficulty')).toBeInTheDocument();
    expect(screen.getByText('Acknowledge & Save Notes')).toBeInTheDocument();
  });
});
