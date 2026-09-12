import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { EthicsModal } from '../components/EthicsModal';

describe('SAATHI Ethics and Privacy Guardrails', () => {
  it('EthicsModal displays strict non-surveillance and non-medical boundaries', () => {
    render(<EthicsModal isOpen={true} onClose={() => {}} />);

    expect(screen.getByText('SAATHI Ethical & Operational Governance')).toBeInTheDocument();
    expect(screen.getByText('1. Non-Medical Decision Support Only')).toBeInTheDocument();
    expect(screen.getByText('2. Strict Non-Surveillance Commitment')).toBeInTheDocument();
    expect(screen.getByText('3. Privacy by Design & Pseudonymous Identity')).toBeInTheDocument();
    expect(screen.getByText('4. Human-in-the-Loop Governance')).toBeInTheDocument();
  });

  it('verifies absence of forbidden clinical and surveillance terms', () => {
    const { container } = render(<EthicsModal isOpen={true} onClose={() => {}} />);
    const textContent = container.textContent || '';

    // Forbidden terms must not be presented as diagnoses or capabilities
    expect(textContent).not.toContain('Depression Detected');
    expect(textContent).not.toContain('Mentally Ill');
    expect(textContent).not.toContain('Psychological Failure');
    expect(textContent).not.toContain('Dangerous Employee');
    expect(textContent).not.toContain('Stress Diagnosis');
  });
});
