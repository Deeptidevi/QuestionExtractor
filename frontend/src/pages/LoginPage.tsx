import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Layers, Loader2, Sparkles, ArrowRight, Lock, Mail } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { success, error } = useToast();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      error('Missing credentials', 'Please provide both email and password.');
      return;
    }

    setIsSubmitting(true);
    try {
      await login({ username: email, password });
      success('Welcome back!', 'Logged in successfully.');
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      const msg = err.response?.data?.error?.message || 'Incorrect email or password.';
      error('Authentication Failed', msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDemoLogin = () => {
    setEmail('demo_admin@docuquest.ai');
    setPassword('SecurePassword123!');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-surface-50 via-brand-50/20 to-indigo-50/30">
      <div className="w-full max-w-md card-panel p-8 bg-white/95 backdrop-blur-md shadow-xl rounded-2xl border border-surface-200">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md mb-3">
            <Layers className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-surface-900 tracking-tight">DocuQuest</h2>
          <p className="text-xs text-surface-500 mt-1">Sign in to your document intelligence workspace</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-surface-700 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@organization.com"
                required
                className="w-full pl-10 pr-3.5 py-2.5 bg-surface-50 border border-surface-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-sm transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-surface-700 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full pl-10 pr-3.5 py-2.5 bg-surface-50 border border-surface-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-sm transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full btn-primary py-2.5 text-sm font-semibold shadow-md mt-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Signing in...
              </>
            ) : (
              <>
                Sign In
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Demo Shortcut */}
        <div className="mt-6 pt-5 border-t border-surface-100 flex flex-col items-center gap-3">
          <button
            type="button"
            onClick={handleDemoLogin}
            className="text-xs font-semibold text-brand-600 hover:text-brand-700 hover:underline flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Fill Demo Credentials
          </button>

          <p className="text-xs text-surface-500">
            Don't have an account?{' '}
            <Link to="/register" className="font-semibold text-brand-600 hover:underline">
              Create account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
