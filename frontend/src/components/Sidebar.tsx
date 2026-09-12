import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  ShieldAlert,
  BarChart3,
  HeartPulse,
  History,
  Lock,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { role } = useAuth();

  const navItems = [
    {
      to: '/welfare',
      label: 'Welfare Officer Dashboard',
      subtitle: 'Triage & Personnel Reviews',
      icon: LayoutDashboard,
      roles: ['WELFARE_OFFICER', 'ADMIN']
    },
    {
      to: '/commander',
      label: 'Commander Overview',
      subtitle: 'Unit Aggregate Metrics',
      icon: ShieldAlert,
      roles: ['COMMANDER', 'ADMIN']
    },
    {
      to: '/analyst',
      label: 'Analytics & Trends',
      subtitle: 'Workload & Distribution',
      icon: BarChart3,
      roles: ['ANALYST', 'ADMIN']
    },
    {
      to: '/portal',
      label: 'Personnel Portal',
      subtitle: 'Self Check-in & Companion',
      icon: HeartPulse,
      roles: ['PERSONNEL']
    },
    {
      to: '/audit',
      label: 'Audit & Compliance',
      subtitle: 'Security & Access Logs',
      icon: History,
      roles: ['ADMIN']
    }
  ];

  const allowedItems = navItems.filter(item => !role || item.roles.includes(role));

  return (
    <aside className="w-64 bg-white border-r border-saathi-border p-3.5 shrink-0 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-85px)] shadow-gov">
      <div className="space-y-4">
        <div>
          <div className="text-[10px] font-bold uppercase tracking-wider text-saathi-primary px-3 py-1 bg-saathi-primarySubtle rounded mb-2 border border-saathi-secondaryLight">
            Portal Navigation
          </div>
          <nav className="space-y-1">
            {allowedItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-md text-xs font-semibold transition-all border ${
                      isActive
                        ? 'bg-saathi-primary text-white border-saathi-primary shadow-sm'
                        : 'text-saathi-textDark hover:text-saathi-primary hover:bg-saathi-primarySubtle border-transparent'
                    }`
                  }
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 shrink-0" />
                    <div>
                      <div className="font-bold text-xs leading-tight">{item.label}</div>
                      <div className="text-[10px] opacity-80 font-normal leading-tight">{item.subtitle}</div>
                    </div>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 opacity-60" />
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer Security Badge */}
      <div className="p-3 rounded-md bg-saathi-bg border border-saathi-border text-[11px] text-saathi-textMuted space-y-1">
        <div className="flex items-center gap-1.5 font-bold text-saathi-textDark">
          <Lock className="w-3.5 h-3.5 text-saathi-primary" />
          <span>Role-Based Access Control</span>
        </div>
        <p className="text-[10px] text-saathi-textMuted leading-normal">
          Authorized session. Cryptographic JWT verification enforced on all endpoints.
        </p>
      </div>
    </aside>
  );
};
