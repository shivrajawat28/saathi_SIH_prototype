import React from 'react';
import { PriorityTier } from '../types';

interface PriorityBadgeProps {
  priority?: PriorityTier | string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({
  priority = 'GREEN',
  size = 'md',
  showLabel = true
}) => {
  const p = priority.toUpperCase();

  const config = {
    GREEN: {
      bg: 'bg-emerald-50',
      border: 'border-emerald-300',
      text: 'text-emerald-800',
      dot: 'bg-emerald-600',
      label: 'Stable Rhythm (GREEN)',
      short: 'GREEN'
    },
    YELLOW: {
      bg: 'bg-amber-50',
      border: 'border-amber-300',
      text: 'text-amber-800',
      dot: 'bg-amber-600',
      label: 'Early Strain (YELLOW)',
      short: 'YELLOW'
    },
    ORANGE: {
      bg: 'bg-orange-50',
      border: 'border-orange-300',
      text: 'text-orange-800',
      dot: 'bg-orange-600',
      label: 'Elevated Strain (ORANGE)',
      short: 'ORANGE'
    },
    RED: {
      bg: 'bg-red-50',
      border: 'border-red-300',
      text: 'text-red-800',
      dot: 'bg-red-600',
      label: 'Priority Review (RED)',
      short: 'RED'
    },
    INSUFFICIENT_DATA: {
      bg: 'bg-slate-100',
      border: 'border-slate-300',
      text: 'text-slate-700',
      dot: 'bg-slate-500',
      label: 'Insufficient Data',
      short: 'INSUFFICIENT DATA'
    }
  }[p] || {
    bg: 'bg-slate-100',
    border: 'border-slate-300',
    text: 'text-slate-700',
    dot: 'bg-slate-500',
    label: p,
    short: p
  };

  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5 font-bold',
    md: 'text-xs px-2.5 py-1 gap-2 font-bold',
    lg: 'text-sm px-3.5 py-1.5 gap-2.5 font-bold'
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded border ${config.bg} ${config.border} ${config.text} ${sizeClasses}`}
      title={`Support Priority Tier: ${config.label}`}
    >
      <span className={`w-2 h-2 rounded-full ${config.dot}`} />
      <span>{showLabel ? config.label : config.short}</span>
    </span>
  );
};
