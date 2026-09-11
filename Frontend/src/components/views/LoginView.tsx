import React, { useState } from 'react';
import { Mail, Lock, AlertCircle, ShieldCheck, CheckCircle2, User, KeyRound, Sparkles } from 'lucide-react';
import { useInvestigation, DEMO_USERS_MAP } from '../../context/InvestigationContext';
import { UserRole } from '../../types';

export const LoginView: React.FC = () => {
  const { loginUser, theme } = useInvestigation();
  const isLight = theme === 'light';

  const [email, setEmail] = useState(DEMO_USERS_MAP['Investigator'].email);
  const [password, setPassword] = useState(DEMO_USERS_MAP['Investigator'].password);
  const [selectedRole, setSelectedRole] = useState<UserRole>('Investigator');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSelectDemoRole = (role: UserRole) => {
    setSelectedRole(role);
    const demo = DEMO_USERS_MAP[role];
    setEmail(demo.email);
    setPassword(demo.password);
    setErrorMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email.trim()) {
      setErrorMessage('Please enter an authorized email address.');
      return;
    }

    if (!password.trim()) {
      setErrorMessage('Please enter your password.');
      return;
    }

    setIsLoading(true);

    try {
      await loginUser(email, password, selectedRole);
    } catch (error: any) {
      if (error.response && error.response.status === 401) {
        setErrorMessage('Incorrect email or password.');
      } else {
        setErrorMessage('Authentication service unavailable. Please try again later.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`min-h-screen w-full flex items-center justify-center p-4 relative overflow-hidden select-none font-sans ${
      isLight ? 'bg-gradient-to-br from-indigo-50/70 via-[#F8FAFC] to-blue-50/70 text-slate-800' : 'bg-[#050507] text-white'
    }`}>
      {/* Tactical Ambient Glow Effects */}
      {isLight ? (
        <>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-indigo-200/30 via-blue-200/20 to-transparent rounded-full blur-[140px] pointer-events-none" />
          <div className="absolute top-1/4 right-1/4 w-[350px] h-[350px] bg-blue-100/40 rounded-full blur-[100px] pointer-events-none" />
          <div className="absolute -bottom-20 -left-20 w-[400px] h-[400px] bg-indigo-100/30 rounded-full blur-[120px] pointer-events-none" />
          <div className="absolute inset-0 bg-[radial-gradient(#CBD5E1_1px,transparent_1px)] [background-size:24px_24px] opacity-40 pointer-events-none" />
        </>
      ) : (
        <>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-[#CA8A04]/15 via-[#FACC15]/10 to-transparent rounded-full blur-[140px] pointer-events-none" />
          <div className="absolute top-1/4 right-1/4 w-[350px] h-[350px] bg-[#EAB308]/10 rounded-full blur-[100px] pointer-events-none" />
          <div className="absolute -bottom-20 -left-20 w-[400px] h-[400px] bg-[#18181C]/40 rounded-full blur-[120px] pointer-events-none" />
          <div className="absolute inset-0 bg-[radial-gradient(#18181C_1px,transparent_1px)] [background-size:24px_24px] opacity-25 pointer-events-none" />
        </>
      )}

      {/* Main Glassmorphic Login Card matching User Image */}
      <div className={`w-full max-w-md rounded-[2.5rem] p-8 sm:p-10 relative z-10 backdrop-blur-2xl space-y-6 ${
        isLight
          ? 'bg-white/95 border border-indigo-100 shadow-[0_25px_60px_rgba(79,70,229,0.12)]'
          : 'glass-panel border border-white/10 shadow-[0_25px_60px_rgba(0,0,0,0.85)]'
      }`}>
        {/* Header */}
        <div className="text-center space-y-1">
          <h1 className={`text-4xl font-bold tracking-tight font-sans ${isLight ? 'text-slate-900' : 'text-white'}`}>
            Log in
          </h1>
        </div>

        {/* Demo Persona Pills Selector (3 Roles: Investigator, Analyst, Admin) */}
        <div className="space-y-2 pt-1">
          <div className={`text-[10px] font-mono uppercase tracking-[0.2em] font-bold text-center flex items-center justify-center space-x-1.5 ${
            isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'
          }`}>
            <Sparkles className={`w-3.5 h-3.5 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
            <span>Select 1 of 3 Authorized Personas</span>
          </div>
          <div className="grid grid-cols-3 gap-1.5 text-xs font-mono">
            {(['Investigator', 'Intelligence Analyst', 'System Administrator'] as UserRole[]).map((r) => {
              const active = selectedRole === r;
              const shortLabel =
                r === 'Investigator'
                  ? 'Investigator'
                  : r === 'Intelligence Analyst'
                  ? 'Analyst'
                  : 'Admin';
              const icon = r === 'Investigator' ? '🕵️' : r === 'Intelligence Analyst' ? '📊' : '⚙️';
              return (
                <button
                  key={r}
                  type="button"
                  onClick={() => handleSelectDemoRole(r)}
                  className={`py-2.5 px-1.5 rounded-2xl text-center border transition-all cursor-pointer truncate ${
                    active
                      ? isLight
                        ? 'bg-[#4F46E5] border-[#4F46E5] text-white font-bold shadow-[0_4px_16px_rgba(79,70,229,0.35)]'
                        : 'bg-[#FACC15]/20 border-[#FACC15] text-[#FACC15] font-bold shadow-[0_0_12px_rgba(250,204,21,0.4)]'
                      : isLight
                      ? 'bg-indigo-50/40 border-indigo-200/80 text-slate-700 font-semibold hover:bg-indigo-50 hover:border-indigo-400 hover:text-[#4F46E5] shadow-xs'
                      : 'bg-[#0D0D10]/80 border-white/10 text-[#94A3B8] hover:text-white hover:border-white/20'
                  }`}
                  title={r}
                >
                  <span className="mr-1">{icon}</span>
                  <span>{shortLabel}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          {errorMessage && (
            <div className={`p-3 rounded-2xl border text-xs flex items-center space-x-2 ${
              isLight
                ? 'bg-rose-50 border-rose-200 text-rose-700'
                : 'bg-rose-950/50 border-rose-800/60 text-rose-300'
            }`}>
              <AlertCircle className={`w-4 h-4 shrink-0 ${isLight ? 'text-rose-600' : 'text-rose-400'}`} />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Email Address Input */}
          <div className="relative">
            <Mail className={`w-4 h-4 absolute left-4 top-3.5 ${isLight ? 'text-slate-400' : 'text-[#64748B]'}`} />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              className={`w-full pl-11 pr-4 py-3.5 rounded-full text-xs transition-all font-mono ${
                isLight
                  ? 'bg-white border border-slate-200 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[#4F46E5] focus:ring-2 focus:ring-[#4F46E5]/20 shadow-xs'
                  : 'bg-[#0D0D10]/80 border border-white/10 text-[#F8FAFC] placeholder:text-[#475569] focus:outline-none focus:border-[#FACC15] focus:ring-1 focus:ring-[#FACC15]'
              }`}
            />
          </div>

          {/* Password Input */}
          <div className="relative">
            <Lock className={`w-4 h-4 absolute left-4 top-3.5 ${isLight ? 'text-slate-400' : 'text-[#64748B]'}`} />
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className={`w-full pl-11 pr-11 py-3.5 rounded-full text-xs transition-all font-mono ${
                isLight
                  ? 'bg-white border border-slate-200 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[#4F46E5] focus:ring-2 focus:ring-[#4F46E5]/20 shadow-xs'
                  : 'bg-[#0D0D10]/80 border border-white/10 text-[#F8FAFC] placeholder:text-[#475569] focus:outline-none focus:border-[#FACC15] focus:ring-1 focus:ring-[#FACC15]'
              }`}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className={`absolute right-4 top-3.5 transition-colors cursor-pointer ${
                isLight ? 'text-indigo-600 hover:text-indigo-800' : 'text-[#FACC15] hover:text-white'
              }`}
              title={showPassword ? 'Hide password' : 'Show password'}
            >
              <Lock className="w-4 h-4" />
            </button>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-3.5 rounded-full font-bold text-sm transition-all cursor-pointer flex items-center justify-center space-x-2 ${
              isLight
                ? 'bg-[#4F46E5] hover:bg-[#4338CA] text-white border-transparent shadow-[0_4px_16px_rgba(79,70,229,0.35)] hover:shadow-[0_4px_22px_rgba(79,70,229,0.5)] active:scale-[0.99]'
                : 'bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] border border-[#FACC15] shadow-lg hover:shadow-[0_0_20px_rgba(250,204,21,0.4)]'
            }`}
          >
            {isLoading ? (
              <span className="inline-flex items-center space-x-2 text-xs font-mono">
                <span className={`w-3.5 h-3.5 border-2 rounded-full animate-spin ${
                  isLight ? 'border-white/30 border-t-white' : 'border-[#050507]/30 border-t-[#050507]'
                }`} />
                <span>Authenticating Session...</span>
              </span>
            ) : (
              <span>Log in</span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
