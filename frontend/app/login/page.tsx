"use client";

import { useState } from "react";
import { useAuth } from "../../hooks/use-auth";
import { Terminal, Shield, Cpu } from "lucide-react";

export default function LoginPage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [error, setError] = useState("");
  const [formLoading, setFormLoading] = useState(false);
  const { login, signup } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setFormLoading(true);

    try {
      if (isSignUp) {
        await signup(name, email, password, company);
      } else {
        await login(email, password);
      }
    } catch (err: any) {
      setError(err.message || "An error occurred during authentication");
      setFormLoading(false);
    }
  };

  return (
    <div className="flex flex-1 min-h-screen bg-slate-950 relative overflow-hidden items-center justify-center px-4 py-12">
      {/* Decorative gradient background blobs */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-indigo-900/10 blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-96 h-96 rounded-full bg-fuchsia-900/10 blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md space-y-8 z-10">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-950/40 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <Cpu className="w-3.5 h-3.5" /> AI agent orchestrator
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 via-slate-100 to-fuchsia-200">
            RecruitAgent
          </h1>
          <p className="text-sm text-slate-400">
            {isSignUp ? "Create a client account to launch campaigns" : "Sign in to manage candidate workflows"}
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800 rounded-2xl p-8 shadow-2xl shadow-slate-950/50">
          <form onSubmit={handleSubmit} className="space-y-5">
            {isSignUp && (
              <>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Jane Client"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 text-sm rounded-xl px-4 py-3 outline-none transition-all placeholder:text-slate-600"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="TechCorp Solutions"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 text-sm rounded-xl px-4 py-3 outline-none transition-all placeholder:text-slate-600"
                  />
                </div>
              </>
            )}

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="client@techcorp.com"
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 text-sm rounded-xl px-4 py-3 outline-none transition-all placeholder:text-slate-600"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-100 text-sm rounded-xl px-4 py-3 outline-none transition-all placeholder:text-slate-600"
              />
            </div>

            {error && (
              <div className="flex gap-2 p-3.5 rounded-xl border border-red-500/20 bg-red-950/20 text-red-400 text-xs leading-5">
                <Shield className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={formLoading}
              className="w-full relative group overflow-hidden bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-medium text-sm rounded-xl py-3.5 shadow-lg shadow-indigo-900/30 transition-all active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none"
            >
              {formLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                  <span>Processing...</span>
                </div>
              ) : isSignUp ? (
                "Create Client Account"
              ) : (
                "Authenticate & Sign In"
              )}
            </button>
          </form>

          {/* Tab switches */}
          <div className="mt-6 pt-6 border-t border-slate-800 text-center text-xs text-slate-400">
            {isSignUp ? (
              <p>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsSignUp(false);
                    setError("");
                  }}
                  className="text-indigo-400 font-semibold hover:underline"
                >
                  Sign In
                </button>
              </p>
            ) : (
              <p>
                Don&apos;t have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsSignUp(true);
                    setError("");
                  }}
                  className="text-indigo-400 font-semibold hover:underline"
                >
                  Create Account
                </button>
              </p>
            )}
          </div>
        </div>

        {/* Developer Sandbox Notice */}
        <div className="flex gap-2.5 items-center justify-center text-[11px] text-slate-600 uppercase tracking-widest font-semibold">
          <Terminal className="w-3.5 h-3.5" /> Secures session via SHA256 HMAC
        </div>
      </div>
    </div>
  );
}
