import React from 'react';
import { X, ShieldCheck, Lock, EyeOff, Scale, CheckCircle2 } from 'lucide-react';

interface EthicsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EthicsModal: React.FC<EthicsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="bg-saathi-card border-2 border-saathi-primary w-full max-w-2xl rounded-lg shadow-gov-lg overflow-hidden animate-in fade-in zoom-in duration-150">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-saathi-primary text-white border-b border-saathi-primaryDark">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded bg-saathi-primaryDark text-saathi-saffron border border-saathi-primaryLight">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">SAATHI Ethical & Operational Governance</h3>
              <p className="text-[11px] text-saathi-secondaryLight">SIH Problem Statement 26186 — MHA / Police II (CRPF)</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-saathi-saffron p-1 rounded hover:bg-saathi-primaryDark transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-3.5 max-h-[70vh] overflow-y-auto text-xs text-saathi-textDark leading-relaxed bg-saathi-bg">
          
          <div className="p-3.5 rounded border border-saathi-border bg-white shadow-xs space-y-1.5">
            <h4 className="font-bold text-saathi-primary text-xs flex items-center gap-2">
              <Scale className="w-4 h-4 text-saathi-saffron" />
              1. Non-Medical Decision Support Only
            </h4>
            <p className="text-saathi-textMuted">
              SAATHI is an operational decision support system that predicts <strong>Welfare Support Priority</strong>. It does <strong>not</strong> provide medical diagnoses, psychiatric evaluations, or psychological fitness certifications.
            </p>
          </div>

          <div className="p-3.5 rounded border border-saathi-border bg-white shadow-xs space-y-1.5">
            <h4 className="font-bold text-saathi-primary text-xs flex items-center gap-2">
              <EyeOff className="w-4 h-4 text-saathi-saffron" />
              2. Strict Non-Surveillance Commitment
            </h4>
            <p className="text-saathi-textMuted">
              The system explicitly excludes video surveillance, facial emotion recognition, keystroke monitoring, private messaging inspection, voice stress/pitch analysis, and real-time GPS tracking.
            </p>
          </div>

          <div className="p-3.5 rounded border border-saathi-border bg-white shadow-xs space-y-1.5">
            <h4 className="font-bold text-saathi-primary text-xs flex items-center gap-2">
              <Lock className="w-4 h-4 text-saathi-saffron" />
              3. Privacy by Design & Pseudonymous Identity
            </h4>
            <p className="text-saathi-textMuted">
              Personnel are referenced via pseudonymous IDs (<code className="text-saathi-primary font-bold">P-000001</code> to <code className="text-saathi-primary font-bold">P-001470</code>). Commanders receive aggregate unit welfare distributions and are strictly restricted from viewing individual personnel predictions or conversation transcripts.
            </p>
          </div>

          <div className="p-3.5 rounded border border-saathi-border bg-white shadow-xs space-y-1.5">
            <h4 className="font-bold text-saathi-primary text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-saathi-saffron" />
              4. Human-in-the-Loop Governance
            </h4>
            <p className="text-saathi-textMuted">
              AI generates decision support recommendations and factor attributions. Authorized human welfare officers remain solely responsible for validating recommendations and initiating supportive, non-punitive interventions.
            </p>
          </div>

          <div className="text-[11px] text-saathi-textSubtle pt-2 border-t border-saathi-border">
            <strong>DEMO ENVIRONMENT NOTICE:</strong> Longitudinal operational datasets used in this prototype are synthetic, privacy-preserving simulations engineered for SIH demonstration.
          </div>
        </div>

        {/* Footer */}
        <div className="p-3.5 border-t border-saathi-border bg-white flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-bold text-white bg-saathi-primary hover:bg-saathi-primaryLight rounded shadow-xs transition-colors"
          >
            Acknowledge & Close
          </button>
        </div>

      </div>
    </div>
  );
};
