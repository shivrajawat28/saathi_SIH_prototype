import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { PriorityBadge } from '../components/PriorityBadge';
import { ScoreMeter } from '../components/ScoreMeter';
import { BaselineComparisonCard } from '../components/BaselineComparisonCard';
import { FactorAttributionList } from '../components/FactorAttributionList';
import { RecommendationList } from '../components/RecommendationList';
import { TimelineItem, TopFactor, WelfareRecommendation } from '../types';

describe('SAATHI Reusable Core Components', () => {
  it('renders PriorityBadge with accessible labels', () => {
    const { rerender } = render(<PriorityBadge priority="RED" />);
    expect(screen.getByText('Priority Review (RED)')).toBeInTheDocument();

    rerender(<PriorityBadge priority="GREEN" />);
    expect(screen.getByText('Stable Rhythm (GREEN)')).toBeInTheDocument();

    rerender(<PriorityBadge priority="YELLOW" />);
    expect(screen.getByText('Early Strain (YELLOW)')).toBeInTheDocument();

    rerender(<PriorityBadge priority="ORANGE" />);
    expect(screen.getByText('Elevated Strain (ORANGE)')).toBeInTheDocument();
  });

  it('renders ScoreMeter with 0-100 score and explicit disclaimers', () => {
    render(
      <ScoreMeter
        score={82.0}
        priority="RED"
        reliability={0.87}
        completeness={0.92}
      />
    );

    expect(screen.getByText('82.0')).toBeInTheDocument();
    expect(screen.getByText('Welfare Support Priority Score')).toBeInTheDocument();
    expect(screen.getByText('87%')).toBeInTheDocument();
    expect(screen.getByText('92%')).toBeInTheDocument();
  });

  it('renders BaselineComparisonCard comparing personal baseline with current observed', () => {
    const mockRecord: TimelineItem = {
      month_idx: 12,
      date: '2024-12',
      support_score: 82,
      support_priority: 'RED',
      duty_hours: 210.5,
      duty_hours_baseline: 160.0,
      duty_pct_change: 31.6,
      night_shifts: 8,
      night_shifts_baseline: 2.0,
      night_shifts_pct_change: 300.0,
      rest_hours: 55.0,
      workload_score: 88.0,
      days_since_prev_leave: 120,
      is_deployed: true,
      took_leave: false,
    };

    render(<BaselineComparisonCard currentRecord={mockRecord} />);

    expect(screen.getByText('Monthly Duty Hours')).toBeInTheDocument();
    expect(screen.getByText('210.5 hrs')).toBeInTheDocument();
    expect(screen.getByText('160.0 hrs')).toBeInTheDocument();
    expect(screen.getByText('+31.6%')).toBeInTheDocument();
  });

  it('renders FactorAttributionList with non-clinical, welfare-focused terminology', () => {
    const factors: TopFactor[] = [
      {
        factor: 'Night Shift Load',
        contribution: 0.28,
        direction: 'increase',
      },
      {
        factor: 'Rest Hours Deficit',
        contribution: -0.19,
        direction: 'decrease',
      }
    ];

    render(<FactorAttributionList factors={factors} />);

    expect(screen.getByText('Why Did This Score Change?')).toBeInTheDocument();
    expect(screen.getByText('Night Shift Load')).toBeInTheDocument();
    expect(screen.getByText('Rest Hours Deficit')).toBeInTheDocument();
    expect(screen.getByText('28% impact')).toBeInTheDocument();
  });

  it('renders RecommendationList with actionable non-punitive options', () => {
    const recommendations: WelfareRecommendation[] = [
      {
        type: 'WORKLOAD_REVIEW',
        priority: 'HIGH',
        reason: 'Duty hours significantly deviate (+31.6%) from personal baseline.',
      },
      {
        type: 'RECOVERY_LEAVE',
        priority: 'MEDIUM',
        reason: 'Rest hours have declined below personal recovery thresholds.',
      }
    ];

    render(<RecommendationList recommendations={recommendations} />);

    expect(screen.getByText('Recommended Welfare Actions')).toBeInTheDocument();
    expect(screen.getByText('WORKLOAD REVIEW')).toBeInTheDocument();
    expect(screen.getByText('RECOVERY LEAVE')).toBeInTheDocument();
    expect(screen.getByText('Duty hours significantly deviate (+31.6%) from personal baseline.')).toBeInTheDocument();
  });
});
