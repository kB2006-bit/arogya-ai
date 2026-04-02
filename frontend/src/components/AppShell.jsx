import { HeartPulse, Languages, LogOut, MapPinned, MessageCircleHeart, ShieldPlus, History } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useAppContext } from "@/context/AppContext";
import { translations } from "@/lib/translations";


const navLinkClass = ({ isActive }) =>
  `rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
    isActive ? "bg-primary text-white" : "text-slate-700 hover:bg-primary-light hover:text-primary"
  }`;


export const AppShell = () => {
  const navigate = useNavigate();
  const { isAuthenticated, language, logout, switchLanguage } = useAppContext();
  const t = translations[language];

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top_left,rgba(216,226,211,0.9),transparent_35%),radial-gradient(circle_at_top_right,rgba(221,207,180,0.65),transparent_28%),linear-gradient(180deg,#fdfbf7_0%,#f6f3ec_100%)] text-slate-900">
      <div className="mx-auto min-h-screen max-w-7xl px-4 pb-10 pt-4 sm:px-6 lg:px-8">
        <header className="sticky top-4 z-50 border border-border/80 bg-background/90 px-4 py-4 shadow-sm backdrop-blur-xl sm:px-6" data-testid="app-header">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-white" data-testid="app-logo">
                <HeartPulse className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.3em] text-[#8E9B86]">{t.landing.eyebrow}</p>
                <h1 className="font-heading text-2xl font-semibold text-slate-900">{t.appName}</h1>
                <p className="text-sm text-slate-600" data-testid="app-tagline">{t.tagline}</p>
              </div>
            </div>

            <div className="flex flex-col gap-3 md:flex-row md:items-center">
              <nav className="flex flex-wrap gap-2" data-testid="primary-navigation">
                <NavLink className={navLinkClass} data-testid="nav-home-link" end to="/">{t.navigation.home}</NavLink>
                {isAuthenticated ? (
                  <>
                    <NavLink className={navLinkClass} data-testid="nav-dashboard-link" end to="/dashboard">{t.navigation.dashboard}</NavLink>
                    <NavLink className={navLinkClass} data-testid="nav-history-link" end to="/history">
                      <History className="h-4 w-4 inline mr-1" />
                      {language === 'hi' ? 'इतिहास' : 'History'}
                    </NavLink>
                    <NavLink className={navLinkClass} data-testid="nav-clinics-link" end to="/clinics">{t.navigation.clinics}</NavLink>
                  </>
                ) : (
                  <>
                    <NavLink className={navLinkClass} data-testid="nav-login-link" to="/login">{t.navigation.login}</NavLink>
                    <NavLink className={navLinkClass} data-testid="nav-signup-link" to="/signup">{t.navigation.signup}</NavLink>
                  </>
                )}
              </nav>

              <div className="flex flex-wrap items-center gap-2">
                <div className="flex items-center gap-2 rounded-full border border-border bg-white/90 px-2 py-1" data-testid="language-toggle-group">
                  <Languages className="h-4 w-4 text-slate-500" />
                  <button className={`rounded-full px-3 py-1 text-sm font-semibold ${language === "en" ? "bg-primary text-white" : "text-slate-600"}`} data-testid="language-toggle-en" onClick={() => switchLanguage("en")} type="button">EN</button>
                  <button className={`rounded-full px-3 py-1 text-sm font-semibold ${language === "hi" ? "bg-primary text-white" : "text-slate-600"}`} data-testid="language-toggle-hi" onClick={() => switchLanguage("hi")} type="button">हिं</button>
                </div>

                {isAuthenticated && (
                  <Button className="rounded-full bg-primary px-5 py-2 text-white hover:bg-primary/90" data-testid="logout-button" onClick={handleLogout} type="button">
                    <LogOut className="h-4 w-4" />
                    {t.navigation.logout}
                  </Button>
                )}
              </div>
            </div>
          </div>
        </header>

        <div className="py-8 sm:py-10">
          <div className="grid gap-4 rounded-[2rem] border border-border/70 bg-white/70 p-4 shadow-[0_24px_90px_rgba(74,103,65,0.08)] backdrop-blur-md lg:grid-cols-[1fr_280px] lg:p-6">
            <main className="min-w-0" data-testid="page-content">
              <Outlet />
            </main>
            <aside className="grid gap-4 self-start lg:sticky lg:top-28">
              <div className="rounded-[1.75rem] border border-border bg-[#f7f5ef] p-6" data-testid="sidebar-guidance-card">
                <div className="mb-4 inline-flex rounded-full bg-primary-light px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-primary">ArogyaAI</div>
                <h2 className="font-heading text-2xl font-semibold text-slate-900">{t.shell.sideTitle}</h2>
                <p className="mt-3 text-sm leading-7 text-slate-600">{t.shell.sideBody}</p>
              </div>
              <div className="grid gap-3">
                {[
                  { icon: MessageCircleHeart, label: t.navigation.chat, hint: t.landing.cards[0].body },
                  { icon: ShieldPlus, label: t.dashboard.high, hint: t.landing.cards[1].body },
                  { icon: MapPinned, label: t.navigation.clinics, hint: t.landing.cards[2].body },
                ].map((item) => (
                  <div className="rounded-[1.5rem] border border-border bg-white p-4" data-testid={`sidebar-feature-${item.label.toLowerCase().replace(/\s+/g, "-")}`} key={item.label}>
                    <item.icon className="mb-3 h-5 w-5 text-primary" />
                    <p className="font-semibold text-slate-900">{item.label}</p>
                    <p className="mt-1 text-sm leading-6 text-slate-600">{item.hint}</p>
                  </div>
                ))}
              </div>
            </aside>
          </div>
        </div>
      </div>
    </div>
  );
};