import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState<string>('welfare_officer');
  const [password, setPassword] = useState<string>('welfare123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const user = await login(username, password);
      if (user.role === 'COMMANDER') {
        navigate('/commander');
      } else if (user.role === 'ANALYST') {
        navigate('/analyst');
      } else if (user.role === 'PERSONNEL') {
        navigate('/portal');
      } else if (user.role === 'ADMIN') {
        navigate('/welfare');
      } else {
        navigate('/welfare');
      }
    } catch (err: any) {
      console.error('Login failure:', err);
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const setDemoCredentials = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-saathi-bg text-saathi-textDark">
      {/* Top Govt Bar */}
      <div>
        <div className="bg-saathi-bgAlt border-b border-saathi-border text-saathi-textMuted px-4 sm:px-6 py-1.5 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2 font-medium">
            <span className="font-bold text-saathi-textDark">भारत सरकार | Government of India</span>
            <span className="text-saathi-border">|</span>
            <span className="hidden sm:inline">Ministry of Home Affairs (MHA)</span>
          </div>
          <span className="text-[11px] font-semibold text-saathi-primary">Police-II Division (CRPF Support System)</span>
        </div>
        <div className="tricolor-stripe" />
      </div>

      <div className="w-full max-w-lg mx-auto p-4 sm:p-6 my-auto">
        
        {/* Institutional Card */}
        <div className="bg-white border-2 border-saathi-primary rounded-lg shadow-gov-lg overflow-hidden">
          
          {/* Card Header */}
          <div className="bg-saathi-primary p-6 text-center text-white border-b-2 border-saathi-saffron">
            <div className="inline-flex p-3 rounded-lg bg-saathi-primaryDark border border-saathi-primaryLight text-saathi-saffron shadow-sm mb-3">
              <Shield className="w-8 h-8 fill-saathi-saffron/20 stroke-white" />
            </div>
            <h1 className="text-2xl font-black tracking-wider text-white">SAATHI</h1>
            <p className="text-xs text-saathi-secondaryLight mt-1 font-medium">
              AI-Based Personnel Welfare Support & Monitoring Decision System
            </p>
            <div className="inline-block mt-2 text-[10px] font-bold uppercase tracking-wider text-saathi-primaryDark bg-amber-300 px-2.5 py-0.5 rounded shadow-xs">
              SIH Problem Statement 26186
            </div>
          </div>

          {/* Form */}
          <div className="p-6 sm:p-8 space-y-5 bg-white">
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-xs font-bold text-saathi-textDark uppercase tracking-wider mb-1.5">
                  Username / Service ID
                </label>
                <div className="relative">
                  <input
                    id="username"
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full pl-9 pr-3.5 py-2 rounded border border-saathi-border text-saathi-textDark text-xs bg-saathi-bg focus:bg-white focus:outline-none focus:border-saathi-primary focus:ring-1 focus:ring-saathi-primary transition-all font-medium"
                    placeholder="e.g. welfare_officer"
                  />
                  <User className="w-4 h-4 text-saathi-textMuted absolute left-3 top-2.5" />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-xs font-bold text-saathi-textDark uppercase tracking-wider mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-9 pr-3.5 py-2 rounded border border-saathi-border text-saathi-textDark text-xs bg-saathi-bg focus:bg-white focus:outline-none focus:border-saathi-primary focus:ring-1 focus:ring-saathi-primary transition-all font-medium"
                    placeholder="••••••••"
                  />
                  <Lock className="w-4 h-4 text-saathi-textMuted absolute left-3 top-2.5" />
                </div>
              </div>

              {error && (
                <div className="p-3 rounded border border-red-300 bg-red-50 text-xs text-red-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-saathi-saffron hover:bg-saathi-saffronHover text-white font-bold py-2.5 px-4 rounded text-xs transition-colors shadow-sm disabled:opacity-50 cursor-pointer uppercase tracking-wider"
              >
                {loading ? (
                  <span>Authenticating Role...</span>
                ) : (
                  <>
                    <span>Sign In to SAATHI Portal</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Quick Demo Accounts */}
            <div className="pt-4 border-t border-saathi-border">
              <span className="block text-[11px] font-bold uppercase tracking-wider text-saathi-primary mb-2">
                Evaluator / Demo Presets (1-Click Switch)
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => setDemoCredentials('welfare_officer', 'welfare123')}
                  className={`p-2 rounded border text-left transition-all ${username === 'welfare_officer' ? 'bg-saathi-primarySubtle border-saathi-primary text-saathi-primary font-bold' : 'bg-saathi-bg border-saathi-border text-saathi-textMuted hover:border-saathi-primary'}`}
                >
                  <div className="text-[11px] font-bold">Welfare Officer</div>
                  <div className="text-[10px] opacity-75 font-mono">welfare_officer</div>
                </button>

                <button
                  type="button"
                  onClick={() => setDemoCredentials('commander', 'commander123')}
                  className={`p-2 rounded border text-left transition-all ${username === 'commander' ? 'bg-saathi-primarySubtle border-saathi-primary text-saathi-primary font-bold' : 'bg-saathi-bg border-saathi-border text-saathi-textMuted hover:border-saathi-primary'}`}
                >
                  <div className="text-[11px] font-bold">Commander</div>
                  <div className="text-[10px] opacity-75 font-mono">commander</div>
                </button>

                <button
                  type="button"
                  onClick={() => setDemoCredentials('personnel_p13', 'personnel123')}
                  className={`p-2 rounded border text-left transition-all ${username === 'personnel_p13' ? 'bg-amber-50 border-amber-500 text-amber-900 font-bold' : 'bg-saathi-bg border-saathi-border text-saathi-textMuted hover:border-saathi-primary'}`}
                >
                  <div className="text-[11px] font-bold text-saathi-saffron">P-000013 (Demo)</div>
                  <div className="text-[10px] opacity-75 font-mono">personnel_p13</div>
                </button>

                <button
                  type="button"
                  onClick={() => setDemoCredentials('officer_p1', 'personnel123')}
                  className={`p-2 rounded border text-left transition-all ${username === 'officer_p1' ? 'bg-saathi-primarySubtle border-saathi-primary text-saathi-primary font-bold' : 'bg-saathi-bg border-saathi-border text-saathi-textMuted hover:border-saathi-primary'}`}
                >
                  <div className="text-[11px] font-bold">P-000001 (Baseline)</div>
                  <div className="text-[10px] opacity-75 font-mono">officer_p1</div>
                </button>

                <button
                  type="button"
                  onClick={() => setDemoCredentials('analyst', 'analyst123')}
                  className={`p-2 rounded border text-left transition-all ${username === 'analyst' ? 'bg-saathi-primarySubtle border-saathi-primary text-saathi-primary font-bold' : 'bg-saathi-bg border-saathi-border text-saathi-textMuted hover:border-saathi-primary'}`}
                >
                  <div className="text-[11px] font-bold">Analyst</div>
                  <div className="text-[10px] opacity-75 font-mono">analyst</div>
                </button>

                <button
                  type="button"
                  onClick={() => setDemoCredentials('admin', 'admin123')}
                  className={`p-2 rounded border text-left transition-all ${username === 'admin' ? 'bg-saathi-primarySubtle border-saathi-primary text-saathi-primary font-bold' : 'bg-saathi-bg border-saathi-border text-saathi-textMuted hover:border-saathi-primary'}`}
                >
                  <div className="text-[11px] font-bold">Admin / Audit</div>
                  <div className="text-[10px] opacity-75 font-mono">admin</div>
                </button>
              </div>
            </div>

          </div>
        </div>

        {/* Footer info */}
        <p className="text-[11px] text-saathi-textMuted text-center mt-4">
          🔒 Decision Support Aid. AI suggests; authorized humans decide. Zero medical diagnosis.
        </p>
      </div>

      {/* Bottom Govt Footer */}
      <footer className="bg-saathi-primaryDark text-white py-3 px-4 text-center text-xs border-t border-saathi-primary">
        <div className="flex flex-wrap items-center justify-center gap-4 text-saathi-secondaryLight text-[11px]">
          <span>Security Audit: COMPLIANT</span>
          <span>•</span>
          <span>Role-Based Privacy: ENFORCED</span>
          <span>•</span>
          <span>MHA SIH-26186 Reference Architecture</span>
        </div>
      </footer>
    </div>
  );
};
