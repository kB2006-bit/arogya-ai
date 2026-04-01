import { ArrowRight, HeartHandshake, Languages, MapPinned, ShieldAlert, Stethoscope } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useAppContext } from "@/context/AppContext";
import { translations } from "@/lib/translations";


const features = [
  { key: "chat", icon: Stethoscope, labelKey: ["navigation", "chat"] },
  { key: "language", icon: Languages, customLabel: "English + हिंदी" },
  { key: "maps", icon: MapPinned, labelKey: ["navigation", "clinics"] },
  { key: "sos", icon: ShieldAlert, labelKey: ["dashboard", "high"] },
];


export default function LandingPage() {
  const { language } = useAppContext();
  const t = translations[language];

  return (
    <div className="grid gap-8" data-testid="landing-page">
      <section className="overflow-hidden rounded-[2rem] border border-border bg-[#f8f5ef]" data-testid="landing-hero-section">
        <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="px-6 py-8 sm:px-10 sm:py-12">
            <div className="inline-flex rounded-full border border-primary-light bg-white/80 px-4 py-2 text-xs font-bold uppercase tracking-[0.25em] text-primary" data-testid="landing-eyebrow">
              {t.landing.eyebrow}
            </div>
            <h2 className="mt-6 font-heading text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl" data-testid="landing-title">
              {t.landing.title}
            </h2>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-600 sm:text-lg" data-testid="landing-subtitle">
              {t.landing.subtitle}
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              <Button asChild className="rounded-full bg-primary px-6 py-6 text-base text-white hover:bg-primary/90" data-testid="landing-primary-cta">
                <Link to="/login">
                  {t.landing.primaryCta}
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button asChild className="rounded-full border border-border bg-white px-6 py-6 text-base text-primary hover:bg-primary-light" data-testid="landing-secondary-cta" variant="outline">
                <Link to="/signup">{t.landing.secondaryCta}</Link>
              </Button>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {t.landing.cards.map((card) => (
                <div className="rounded-[1.5rem] border border-border bg-white p-5" data-testid={`landing-card-${card.title.toLowerCase().replace(/\s+/g, "-")}`} key={card.title}>
                  <p className="font-semibold text-slate-900">{card.title}</p>
                  <p className="mt-2 text-sm leading-7 text-slate-600">{card.body}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="relative min-h-[420px] overflow-hidden bg-[#e6eadf] p-6 sm:p-8" data-testid="landing-media-section">
            <img
              alt="Trusted doctor for ArogyaAI"
              className="absolute inset-0 h-full w-full object-cover object-center opacity-80"
              data-testid="landing-doctor-image"
              src="https://images.pexels.com/photos/19438563/pexels-photo-19438563.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
            />
            <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(42,51,38,0.05)_0%,rgba(42,51,38,0.8)_100%)]" />

            <div className="relative flex h-full flex-col justify-between">
              <div className="flex justify-end">
                <div className="rounded-[1.5rem] border border-white/20 bg-white/15 p-5 text-white backdrop-blur-md" data-testid="landing-trust-panel">
                  <p className="text-xs font-bold uppercase tracking-[0.25em] text-white/80">ArogyaAI</p>
                  <p className="mt-3 text-lg font-semibold">{t.landing.trustTitle}</p>
                  <p className="mt-2 max-w-xs text-sm leading-7 text-white/85">{t.landing.trustBody}</p>
                </div>
              </div>

              <div className="grid gap-3">
                {features.map((feature) => (
                  <div className="flex items-start gap-3 rounded-[1.25rem] border border-white/15 bg-white/10 p-4 text-white backdrop-blur-sm" data-testid={`feature-highlight-${feature.key}`} key={feature.key}>
                    <feature.icon className="mt-1 h-5 w-5 shrink-0" />
                    <div>
                      <p className="font-semibold">{feature.customLabel || t[feature.labelKey[0]][feature.labelKey[1]]}</p>
                      <p className="text-sm text-white/80">{feature.key === "language" ? t.tagline : t.landing.subtitle}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3" data-testid="landing-benefits-grid">
        {[
          { icon: HeartHandshake, title: t.landing.trustTitle, body: t.landing.trustBody },
          { icon: MapPinned, title: t.navigation.clinics, body: t.landing.cards[2].body },
          { icon: ShieldAlert, title: t.dashboard.high, body: t.landing.cards[1].body },
        ].map((item) => (
          <div className="rounded-[1.75rem] border border-border bg-white p-6" data-testid={`benefit-card-${item.title.toLowerCase().replace(/\s+/g, "-")}`} key={item.title}>
            <item.icon className="h-6 w-6 text-primary" />
            <p className="mt-4 font-heading text-2xl font-semibold text-slate-900">{item.title}</p>
            <p className="mt-3 text-sm leading-7 text-slate-600">{item.body}</p>
          </div>
        ))}
      </section>
    </div>
  );
}