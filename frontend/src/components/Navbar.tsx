import React, { useState } from 'react';
import { Shield, ShieldCheck, LogOut, User, Info, Globe, HelpCircle, PhoneCall, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { EthicsModal } from './EthicsModal';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const [showEthics, setShowEthics] = useState<boolean>(false);
  const [lang, setLang] = useState<'EN' | 'HI'>('EN');

  return (
    <>
      {/* Top Government Utility Bar */}
      <div className="bg-saathi-bgAlt border-b border-saathi-border text-saathi-textMuted px-4 sm:px-6 py-1 text-[11px] font-medium flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 sm:gap-3">
          <span className="font-semibold text-saathi-textDark">भारत सरकार | Government of India</span>
          <span className="text-saathi-border">|</span>
          <span className="hidden md:inline">गृह मंत्रालय | Ministry of Home Affairs</span>
          <span className="text-saathi-border hidden md:inline">|</span>
          <span className="hidden lg:inline text-saathi-primary font-semibold">Police-II Division (CRPF Support Framework)</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-saathi-card border border-saathi-border text-[10px] text-saathi-textDark font-semibold">
            <span className="w-2 h-2 rounded-full bg-saathi-saffron animate-pulse" />
            <span>SIH 26186 Prototype (Synthetic Sandbox)</span>
          </div>

          <button
            onClick={() => setLang(lang === 'EN' ? 'HI' : 'EN')}
            className="hover:text-saathi-primary transition-colors flex items-center gap-1 text-[11px] font-bold"
            title="Toggle Interface Language"
          >
            <Globe className="w-3 h-3 text-saathi-saffron" />
            <span>{lang === 'EN' ? 'हिन्दी' : 'English'}</span>
          </button>
        </div>
      </div>

      {/* Tricolor Subtle Accent Stripe */}
      <div className="tricolor-stripe" />

      {/* Main Institutional Header */}
      <header className="sticky top-0 z-40 bg-saathi-primaryDark text-white border-b border-saathi-primary px-4 sm:px-6 py-3 flex items-center justify-between shadow-gov-md">
        
        {/* Institutional Branding */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-saathi-primary border border-saathi-primaryLight flex items-center justify-center text-saathi-saffron shadow-sm">
            <Shield className="w-6 h-6 fill-saathi-saffron/20 stroke-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-black text-lg tracking-wider text-white">SAATHI</span>
              <span className="text-[10px] font-bold uppercase tracking-wider bg-saathi-saffron text-white px-2 py-0.5 rounded shadow-sm">
                SIH 26186
              </span>
            </div>
            <div className="text-[11px] text-saathi-secondaryLight font-medium tracking-wide">
              Personnel Welfare Intelligence System
            </div>
          </div>
        </div>

        {/* Right Actions & User Context */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowEthics(true)}
            className="flex items-center gap-1.5 text-xs font-semibold text-white bg-saathi-primary hover:bg-saathi-primaryLight border border-saathi-primaryLight px-3 py-1.5 rounded-md transition-colors shadow-sm"
          >
            <ShieldCheck className="w-4 h-4 text-saathi-saffron" />
            <span className="hidden sm:inline">Governance & Ethics</span>
          </button>

          {user && (
            <div className="flex items-center gap-3 pl-3 border-l border-saathi-primaryLight/40">
              <div className="text-right hidden sm:block">
                <div className="text-xs font-bold text-white">{user.full_name || user.username}</div>
                <div className="text-[10px] font-mono text-amber-300 font-semibold">{user.role}</div>
              </div>

              <div className="w-8 h-8 rounded-md bg-saathi-primary border border-saathi-primaryLight flex items-center justify-center text-white">
                <User className="w-4 h-4 text-saathi-saffron" />
              </div>

              <button
                onClick={logout}
                title="Sign Out"
                className="p-1.5 rounded-md text-slate-300 hover:text-white hover:bg-red-900/40 border border-transparent hover:border-red-700/50 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </header>

      <EthicsModal isOpen={showEthics} onClose={() => setShowEthics(false)} />
    </>
  );
};
