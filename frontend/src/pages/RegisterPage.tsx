import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Layers, Loader2, Sparkles, ArrowRight, Lock, Mail, User } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { success, error } = useToast();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || !fullName) {
      error('Missing fields', 'Please fill in all required fields.');
      return;
    }

    setIsSubmitting(true);
    try {
      await register({ email, password, full_name: fullName });
      success('Account Created', 'Welcome to DocuQuest!');
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Registration error:', err);
      const msg = err.response?.data?.error?.message || 'Registration failed. Email might already exist.';
      error('Registration Failed', msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-surface-50 via-brand-50/20 to-indigo-50/30">
      <div className="w-full max-w-md card-panel p-8 bg-white/95 backdrop-blur-md shadow-xl rounded-2xl border border-surface-200">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md mb-3">
            <Layers className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-surface-900 tracking-tight">Create an Account</h2>
          <p className="text-xs text-surface-500 mt-1">Get started with automated question extraction</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-surface-700 mb-1.5">Full Name</label>
            <div className="relative">
              <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Alex Morgan"
                required
                className="w-full pl-10 pr-3.5 py-2.5 bg-surface-50 border border-surface-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-sm transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-surface-700 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@university.edu"
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
                placeholder="At least 8 characters"
                required
                minLength={6}
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
                Creating Account...
              </>
            ) : (
              <>
                Register & Start
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-surface-100 text-center text-xs text-surface-500">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-brand-600 hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
};
