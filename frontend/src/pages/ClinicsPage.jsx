import { useCallback, useEffect, useState } from "react";
import { MapPinned, PhoneCall } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAppContext } from "@/context/AppContext";
import { api, withAuth } from "@/lib/api";
import { translations } from "@/lib/translations";


export default function ClinicsPage() {
  const { token, language } = useAppContext();
  const t = translations[language];
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [loadingMessage, setLoadingMessage] = useState(t.clinics.locating);
  const [clinicData, setClinicData] = useState({ clinics: [], map_embed_url: "", emergency_number: "112" });

  const buildMapUrl = (latitude, longitude) => `https://www.google.com/maps?q=${latitude},${longitude}&z=13&output=embed`;

  const buildFallbackCards = useCallback((latitude, longitude) => [
    {
      id: "fallback-hospital-search",
      name: language === "hi" ? "नज़दीकी अस्पताल खोज" : "Nearby hospital search",
      address: language === "hi" ? "आपकी लोकेशन के आसपास अस्पताल परिणाम तुरंत खोलें।" : "Open live hospital results centered on your current location.",
      distance_km: 0,
      maps_url: `https://www.google.com/maps/search/hospitals/@${latitude},${longitude},14z`,
    },
    {
      id: "fallback-clinic-search",
      name: language === "hi" ? "नज़दीकी क्लिनिक खोज" : "Nearby clinic search",
      address: language === "hi" ? "Google Maps पर क्लिनिक विकल्प देखें।" : "Browse nearby clinic options on Google Maps.",
      distance_km: 0,
      maps_url: `https://www.google.com/maps/search/clinic/@${latitude},${longitude},14z`,
    },
  ], [language]);

  const loadClinics = useCallback(() => {
    setLoading(true);
    setError("");
    setLoadingMessage(t.clinics.locating);

    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        const fallbackPayload = {
          clinics: buildFallbackCards(coords.latitude, coords.longitude),
          map_embed_url: buildMapUrl(coords.latitude, coords.longitude),
          emergency_number: "112",
        };
        setClinicData(fallbackPayload);
        setLoadingMessage(t.clinics.searching);
        const slowTimer = window.setTimeout(() => {
          setLoadingMessage(t.clinics.slowMessage);
        }, 4500);

        try {
          const response = await api.get(`/clinics/nearby?lat=${coords.latitude}&lng=${coords.longitude}`, withAuth(token));
          setClinicData(response.data);
        } catch (requestError) {
          setClinicData(fallbackPayload);
          setError(requestError.response?.data?.detail || t.clinics.slowMessage);
        } finally {
          window.clearTimeout(slowTimer);
          setLoading(false);
        }
      },
      () => {
        setError(t.clinics.denied);
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  }, [buildFallbackCards, t, token]);

  useEffect(() => {
    loadClinics();
  }, [loadClinics]);

  return (
    <div className="grid gap-6" data-testid="clinics-page">
      <section className="rounded-[2rem] border border-border bg-white p-6 sm:p-8" data-testid="clinics-hero-section">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.25em] text-[#8E9B86]">ArogyaAI</p>
            <h2 className="mt-4 font-heading text-4xl font-semibold text-slate-900" data-testid="clinics-title">{t.clinics.title}</h2>
            <p className="mt-3 max-w-2xl text-base leading-8 text-slate-600" data-testid="clinics-subtitle">{t.clinics.subtitle}</p>
          </div>
          <Button className="rounded-full bg-primary px-5 py-6 text-white hover:bg-primary/90" data-testid="clinics-refresh-location-button" onClick={loadClinics} type="button">
            <MapPinned className="h-4 w-4" />
            {loading ? t.clinics.locating : t.clinics.locate}
          </Button>
        </div>

        <div className="mt-6 rounded-[1.5rem] border border-red-200 bg-red-50 p-5" data-testid="clinics-emergency-banner">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="font-semibold text-red-700">{t.clinics.emergency}</p>
              <p className="mt-1 text-sm text-red-600">{t.clinics.helper}</p>
            </div>
            <a className="rounded-full bg-red-600 px-5 py-3 text-sm font-semibold text-white" data-testid="clinics-emergency-call-button" href={`tel:${clinicData.emergency_number || "112"}`}>
              <PhoneCall className="mr-2 inline h-4 w-4" />
              {clinicData.emergency_number || "112"}
            </a>
          </div>
        </div>

        {error ? (
          <div className="mt-6 rounded-[1.5rem] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" data-testid="clinics-error-message">{error}</div>
        ) : null}

        {loading ? (
          <div className="mt-6 rounded-[1.5rem] border border-border bg-[#f8faf6] px-4 py-3 text-sm text-slate-700" data-testid="clinics-loading-status-banner">{loadingMessage}</div>
        ) : null}

        {clinicData.map_embed_url ? (
          <div className="mt-6 overflow-hidden rounded-[1.75rem] border border-border" data-testid="clinics-map-wrapper">
            <iframe className="h-[360px] w-full border-0" data-testid="clinics-map-iframe" src={clinicData.map_embed_url} title={t.clinics.mapTitle} />
          </div>
        ) : null}
      </section>

      <section className="grid gap-4 md:grid-cols-2" data-testid="clinics-results-grid">
        {loading ? (
          <div className="rounded-[1.5rem] border border-border bg-white p-6 text-sm text-slate-600" data-testid="clinics-loading-state">{loadingMessage}</div>
        ) : null}

        {!loading && !error && clinicData.clinics.length === 0 ? (
          <div className="rounded-[1.5rem] border border-dashed border-border bg-white p-6 text-sm text-slate-600" data-testid="clinics-empty-state">{t.clinics.empty}</div>
        ) : null}

        {clinicData.clinics.map((clinic) => (
          <article className="rounded-[1.5rem] border border-border bg-white p-6" data-testid={`clinic-card-${clinic.id}`} key={clinic.id}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-heading text-2xl font-semibold text-slate-900">{clinic.name}</p>
                <p className="mt-2 text-sm leading-7 text-slate-600">{clinic.address}</p>
              </div>
              <span className="rounded-full bg-primary-light px-3 py-1 text-sm font-semibold text-primary" data-testid={`clinic-distance-${clinic.id}`}>{clinic.distance_km} km</span>
            </div>
            <a className="mt-5 inline-flex items-center rounded-full bg-primary px-5 py-3 text-sm font-semibold text-white" data-testid={`clinic-directions-${clinic.id}`} href={clinic.maps_url} rel="noreferrer" target="_blank">
              {t.clinics.directions}
            </a>
          </article>
        ))}
      </section>
    </div>
  );
}