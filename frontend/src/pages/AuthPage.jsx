import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAppContext } from "@/context/AppContext";
import { translations } from "@/lib/translations";


export default function AuthPage({ mode = "login" }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { language, login, signup } = useAppContext();
  const t = translations[language] || translations.en;
  const [form, setForm] = useState({ email: mode === "login" ? "demo@arogyaai.app" : "", password: mode === "login" ? "Arogya123!" : "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const from = location.state?.from?.pathname || "/dashboard";

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      if (mode === "login") {
        await login(form);
      } else {
        await signup(form);
      }
      navigate(from, { replace: true });
    } catch (requestError) {
      console.error("Auth error:", requestError);
      
      // Handle different error types
      let errorMessage = "Unable to continue right now.";
      
      if (requestError.response) {
        // Server responded with error
        if (requestError.response.data?.detail) {
          if (typeof requestError.response.data.detail === 'string') {
            errorMessage = requestError.response.data.detail;
          } else if (Array.isArray(requestError.response.data.detail)) {
            // Pydantic validation errors
            errorMessage = requestError.response.data.detail.map(err => err.msg).join(', ');
          }
        }
      } else if (requestError.request) {
        // Request made but no response
        errorMessage = "Server is not responding. Please try again.";
      } else if (requestError.message) {
        // Error in request setup
        errorMessage = requestError.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl" data-testid={`${mode}-page`}>
      <section className="rounded-[2rem] border border-border bg-white p-6 shadow-sm sm:p-8">
        <div className="rounded-[1.5rem] bg-[#f7f5ef] p-6">
          <p className="text-xs font-bold uppercase tracking-[0.25em] text-[#8E9B86]">ArogyaAI</p>
          <h2 className="mt-4 font-heading text-3xl font-semibold text-slate-900" data-testid={`${mode}-title`}>
            {mode === "login" ? t.auth.loginTitle : t.auth.signupTitle}
          </h2>
          <p className="mt-3 text-sm leading-7 text-slate-600">{t.auth.helper}</p>
          <p className="mt-3 rounded-2xl border border-border bg-white p-4 text-sm text-slate-700" data-testid="auth-demo-credentials">
            {t.auth.demo}
          </p>
        </div>

        <form className="mt-6 grid gap-5" data-testid={`${mode}-form`} onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="email">{t.auth.email}</label>
            <Input className="h-12 rounded-full border-border bg-[#f8faf6] px-5" data-testid={`${mode}-email-input`} id="email" onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} placeholder="name@example.com" type="email" value={form.email} />
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="password">{t.auth.password}</label>
            <Input className="h-12 rounded-full border-border bg-[#f8faf6] px-5" data-testid={`${mode}-password-input`} id="password" onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} placeholder="••••••••" type="password" value={form.password} />
          </div>

          {error ? (
            <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" data-testid="auth-error-message">{error}</div>
          ) : null}

          <Button className="h-12 rounded-full bg-primary text-white hover:bg-primary/90" data-testid={`${mode}-submit-button`} disabled={loading} type="submit">
            {loading ? t.common.loading : mode === "login" ? t.auth.submitLogin : t.auth.submitSignup}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-600">
          <button className="font-semibold text-primary" data-testid="auth-toggle-link" onClick={() => navigate(mode === "login" ? "/signup" : "/login")} type="button">
            {mode === "login" ? t.auth.toggleSignup : t.auth.toggleLogin}
          </button>
        </div>
      </section>
    </div>
  );
}