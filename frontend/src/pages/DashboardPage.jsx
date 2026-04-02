import { useCallback, useEffect, useState } from "react";
import { ArrowRight, Clock3, HeartPulse, MapPinned, ShieldAlert, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LoadingAnalysis } from "@/components/LoadingAnalysis";
import { SymptomResultCard } from "@/components/SymptomResultCard";
import { useAppContext } from "@/context/AppContext";
import { api, withAuth } from "@/lib/api";
import { translations } from "@/lib/translations";
import { saveSymptomCheck, getSymptomHistory } from "@/lib/symptomHistory";


const severityTone = {
  Low: "bg-[#e7f1e3] text-primary",
  Medium: "bg-[#fff2dd] text-[#b45309]",
  High: "bg-[#fee2e2] text-[#b91c1c]",
};


export default function DashboardPage() {
  const { token, language } = useAppContext();
  const t = translations[language];
  const [dashboard, setDashboard] = useState({ total_checks: 0, low_alerts: 0, medium_alerts: 0, high_alerts: 0, recent_checks: [] });
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [clinicsLoading, setClinicsLoading] = useState(false);
  const [clinicsError, setClinicsError] = useState("");
  const [nearbyClinics, setNearbyClinics] = useState([]);
  const [mapEmbedUrl, setMapEmbedUrl] = useState("");
  const [userCoords, setUserCoords] = useState(null);
  const [selectedClinicId, setSelectedClinicId] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [latestResult, setLatestResult] = useState(null);
  const [chatMessages, setChatMessages] = useState([
    {
      id: "dashboard-chat-welcome",
      role: "assistant",
      text: t.chat.assistantWelcome,
      severity: null,
    },
  ]);

  const getSeverityLabel = (severity) => {
    if (severity === "Low") return t.common.severityLow;
    if (severity === "Medium") return t.common.severityMedium;
    return t.common.severityHigh;
  };

  const triggerEmergency = () => {
    window.alert(t.chat.emergencyBanner);
    console.log("Emergency triggered");
  };

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      try {
        const [dashboardResponse, historyResponse] = await Promise.all([
          api.get("/dashboard", withAuth(token)),
          api.get("/history", withAuth(token)),
        ]);
        setDashboard(dashboardResponse.data);
        setHistoryItems(historyResponse.data);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [token]);

  const stats = [
    { key: "total", label: t.dashboard.total, value: dashboard.total_checks, icon: HeartPulse },
    { key: "low", label: t.dashboard.low, value: dashboard.low_alerts, icon: Sparkles },
    { key: "medium", label: t.dashboard.medium, value: dashboard.medium_alerts, icon: Clock3 },
    { key: "high", label: t.dashboard.high, value: dashboard.high_alerts, icon: ShieldAlert },
  ];

  const buildMapUrl = (latitude, longitude) => `https://maps.google.com/maps?q=hospitals+near+${latitude},${longitude}&z=14&output=embed`;
  const buildClinicMapUrl = (latitude, longitude, clinicName) => `https://maps.google.com/maps?q=${encodeURIComponent(clinicName)}@${latitude},${longitude}&z=15&output=embed`;

  const getClinicDistanceLabel = (clinic, index) => {
    if (!userCoords) {
      return `${index + 2} km ${t.clinics.away}`;
    }

    const latDiff = clinic.latitude - userCoords.latitude;
    const lngDiff = clinic.longitude - userCoords.longitude;
    const distance = Math.sqrt(latDiff * latDiff + lngDiff * lngDiff) * 111;
    return `${Math.max(1, Math.round(distance))} km ${t.clinics.away}`;
  };

  const focusClinicOnMap = (clinic) => {
    setSelectedClinicId(clinic.id);
    setMapEmbedUrl(buildClinicMapUrl(clinic.latitude, clinic.longitude, clinic.name));
  };

  const loadNearbyClinics = useCallback(() => {
    setClinicsLoading(true);
    setClinicsError("");

    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        setUserCoords({ latitude: coords.latitude, longitude: coords.longitude });
        setSelectedClinicId("");
        setMapEmbedUrl(buildMapUrl(coords.latitude, coords.longitude));
        try {
          const response = await api.post(
            "/clinics",
            { latitude: coords.latitude, longitude: coords.longitude },
            withAuth(token),
          );
          setNearbyClinics(response.data.clinics || []);
        } catch (error) {
          setClinicsError(error.response?.data?.detail || t.clinics.empty);
        } finally {
          setClinicsLoading(false);
        }
      },
      () => {
        setClinicsError(t.clinics.denied);
        setClinicsLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  }, [t, token]);

  const sendDashboardChat = async () => {
    if (!chatInput.trim()) {
      return;
    }

    const userMessage = {
      id: `dashboard-user-${Date.now()}`,
      role: "user",
      text: chatInput.trim(),
      severity: null,
    };

    setChatMessages((current) => [...current, userMessage]);
    const userInput = chatInput.trim();
    setChatInput("");
    setChatLoading(true);
    setLatestResult(null);

    try {
      console.log('🔍 Symptom Analysis Request:', userInput);
      
      // Use full symptom checker for better results
      const response = await api.post("/symptom-checker", { 
        message: userInput,
        language: language,
        history: []
      }, withAuth(token));
      
      console.log('✅ Symptom Analysis Response:', response.data);
      console.log('📊 Severity:', response.data.severity);
      console.log('🏥 Diagnosis:', response.data.diagnosis);
      
      // Store full result for enhanced display
      setLatestResult({
        ...response.data,
        userMessage: userInput
      });
      
      const assistantMessage = {
        id: `dashboard-ai-${Date.now()}`,
        role: "assistant",
        text: response.data.summary,
        severity: response.data.severity,
        fullResult: response.data,
      };
      
      setChatMessages((current) => [...current, assistantMessage]);
      
      // Save to localStorage history with debugging
      const savedEntry = saveSymptomCheck({
        message: userInput,
        response: response.data.summary,
        severity: response.data.severity,
        diagnosis: response.data.diagnosis,
        summary: response.data.summary,
        next_steps: response.data.next_steps
      });
      
      console.log('💾 Saved to History:', savedEntry);
      console.log('📜 Current History Count:', getSymptomHistory().length);
      
      const historyResponse = await api.get("/history", withAuth(token));
      setHistoryItems(historyResponse.data);
    } catch (error) {
      console.error("❌ Symptom analysis error:", error);
      console.error("Error details:", error.response?.data || error.message);
      setChatMessages((current) => [
        ...current,
        {
          id: `dashboard-ai-error-${Date.now()}`,
          role: "assistant",
          text: error.response?.data?.detail || "Unable to analyze symptoms right now. Please try again.",
          severity: null,
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  useEffect(() => {
    loadNearbyClinics();
  }, [loadNearbyClinics]);

  return (
    <div className="grid gap-6" data-testid="dashboard-page">
      <section className="rounded-[2rem] border border-border bg-white p-6 sm:p-8" data-testid="dashboard-hero-card">
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-[#8E9B86]">ArogyaAI</p>
        <h2 className="mt-4 font-heading text-4xl font-semibold text-slate-900" data-testid="dashboard-title">{t.dashboard.title}</h2>
        <p className="mt-3 max-w-2xl text-base leading-8 text-slate-600" data-testid="dashboard-subtitle">{t.dashboard.subtitle}</p>

        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {stats.map((item) => (
            <div className="rounded-[1.5rem] border border-border bg-[#f8faf6] p-5" data-testid={`dashboard-stat-${item.key}`} key={item.key}>
              <item.icon className="h-5 w-5 text-primary" />
              <p className="mt-4 text-sm font-semibold text-slate-600">{item.label}</p>
              <p className="mt-2 font-heading text-4xl font-semibold text-slate-900">{loading ? "—" : item.value}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2" data-testid="dashboard-actions-grid">
        <section className="rounded-[1.5rem] border border-border bg-primary px-5 py-5 text-white" data-testid="dashboard-chat-panel">
          <span className="text-sm uppercase tracking-[0.2em] text-white/75">ArogyaAI</span>
          <h3 className="mt-2 font-heading text-2xl font-semibold" data-testid="dashboard-chat-title">{t.dashboard.ctaChat}</h3>
          <p className="mt-2 text-sm text-white/90" data-testid="dashboard-chat-helper">{t.chat.subtitle}</p>

          <div className="mt-4 grid gap-3 rounded-[1.25rem] bg-white/10 p-4" data-testid="dashboard-chat-thread">
            {chatMessages.map((message) => (
              <div className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`} data-testid={`dashboard-chat-message-${message.id}`} key={message.id}>
                <div className={`max-w-[85%] rounded-[1.25rem] px-4 py-3 text-sm leading-6 ${message.role === "user" ? "bg-white text-primary" : message.severity === "High" ? "border border-red-300 bg-red-50 text-red-700" : "bg-[#3d5536] text-white"}`}>
                  <p>{message.text}</p>
                  {message.severity ? (
                    <div className="mt-3 grid gap-3">
                      {message.severity === "High" ? (
                        <div className="rounded-xl border border-red-200 bg-red-100 px-3 py-2 text-sm font-semibold text-red-700" data-testid={`dashboard-chat-emergency-banner-${message.id}`}>{t.chat.emergencyBanner}</div>
                      ) : null}
                      <span className={`inline-flex w-fit rounded-full px-3 py-1 text-xs font-semibold ${severityTone[message.severity]}`} data-testid={`dashboard-chat-severity-${message.id}`}>
                        {t.chat.severity}: {getSeverityLabel(message.severity)}
                      </span>
                      {message.severity === "High" ? (
                        <Button className="w-fit rounded-full bg-red-600 px-4 py-2 text-white hover:bg-red-700" data-testid={`dashboard-chat-sos-button-${message.id}`} onClick={triggerEmergency} type="button">
                          {t.chat.sosButton}
                        </Button>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 flex flex-col gap-3 sm:flex-row" data-testid="dashboard-chat-input-row">
            <Input className="h-12 rounded-full border-0 bg-white px-5 text-slate-900" data-testid="dashboard-chat-input" onChange={(event) => setChatInput(event.target.value)} placeholder={t.chat.placeholder} value={chatInput} />
            <Button className="h-12 rounded-full bg-white px-6 text-primary hover:bg-primary-light" data-testid="dashboard-chat-send-button" disabled={chatLoading || !chatInput.trim()} onClick={sendDashboardChat} type="button">
              {chatLoading ? t.common.loading : t.chat.send}
            </Button>
          </div>
        </section>
      </section>

      {/* Enhanced Result Display Section */}
      {chatLoading && (
        <section className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          <LoadingAnalysis message="Analyzing your symptoms with AI..." />
        </section>
      )}
      
      {latestResult && !chatLoading && (
        <section className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          <SymptomResultCard result={latestResult} message={latestResult.userMessage} />
        </section>
      )}

      <section className="grid gap-4 md:grid-cols-2"
          <Link to="/clinics" className="flex flex-col items-start gap-2">
            <span className="text-sm uppercase tracking-[0.2em] text-[#8E9B86]">Emergency-ready</span>
            <span className="font-heading text-2xl font-semibold text-slate-900">{t.dashboard.ctaClinics}</span>
            <span className="flex items-center gap-2 text-sm text-slate-600">{t.clinics.emergency} <ArrowRight className="h-4 w-4" /></span>
          </Link>
        </Button>
      </section>

      <section className="rounded-[2rem] border border-border bg-white p-6 sm:p-8" data-testid="dashboard-nearby-clinics-section">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.25em] text-[#8E9B86]">ArogyaAI</p>
            <h3 className="mt-2 font-heading text-2xl font-semibold text-slate-900" data-testid="dashboard-nearby-clinics-title">{t.clinics.dashboardTitle}</h3>
            <p className="mt-2 text-sm leading-7 text-slate-600" data-testid="dashboard-nearby-clinics-subtitle">{t.clinics.dashboardSubtitle}</p>
          </div>
          <Button className="rounded-full bg-primary px-5 py-3 text-white hover:bg-primary/90" data-testid="dashboard-nearby-clinics-refresh-button" onClick={loadNearbyClinics} type="button">
            <MapPinned className="h-4 w-4" />
            {clinicsLoading ? t.clinics.locating : t.clinics.locate}
          </Button>
        </div>

        {clinicsError ? (
          <div className="mt-5 rounded-[1.25rem] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" data-testid="dashboard-nearby-clinics-error">{clinicsError}</div>
        ) : null}

        <div className="mt-6 grid gap-4">
          <div className="overflow-hidden rounded-[1.5rem] border border-border bg-[#f8faf6]" data-testid="dashboard-nearby-clinics-map-wrapper">
            {mapEmbedUrl ? (
              <iframe className="h-[320px] w-full border-0" data-testid="dashboard-nearby-clinics-map" src={mapEmbedUrl} title={t.clinics.mapTitle} />
            ) : (
              <div className="flex h-[320px] items-center justify-center px-6 text-center text-sm text-slate-500" data-testid="dashboard-nearby-clinics-empty-map">{t.clinics.dashboardEmpty}</div>
            )}
          </div>

          <div className="grid gap-3" data-testid="dashboard-nearby-clinics-list">
            <h4 className="font-heading text-xl font-semibold text-slate-900" data-testid="dashboard-nearby-clinics-list-title">{t.clinics.listTitle}</h4>
            <div className="grid gap-3 md:grid-cols-2">
              {nearbyClinics.map((clinic, index) => (
                <article className={`rounded-[1.25rem] border p-4 ${selectedClinicId === clinic.id ? "border-primary bg-primary-light/40" : "border-border bg-[#fcfcfb]"}`} data-testid={`dashboard-nearby-clinic-card-${clinic.id}`} key={clinic.id}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-semibold text-white" data-testid={`dashboard-nearby-clinic-marker-${clinic.id}`}>{index + 1}</div>
                      <div>
                        <p className="font-semibold text-slate-900" data-testid={`dashboard-nearby-clinic-name-${clinic.id}`}>{clinic.name}</p>
                        <p className="mt-1 text-sm text-slate-500" data-testid={`dashboard-nearby-clinic-distance-${clinic.id}`}>{getClinicDistanceLabel(clinic, index)}</p>
                      </div>
                    </div>
                    <Button className="rounded-full bg-primary px-4 py-2 text-white hover:bg-primary/90" data-testid={`dashboard-nearby-clinic-view-map-${clinic.id}`} onClick={() => focusClinicOnMap(clinic)} type="button">
                      {t.clinics.viewOnMap}
                    </Button>
                  </div>
                </article>
              ))}
            </div>

            {!clinicsLoading && !nearbyClinics.length && !clinicsError ? (
              <div className="rounded-[1.25rem] border border-dashed border-border bg-[#f8faf6] p-4 text-sm text-slate-500" data-testid="dashboard-nearby-clinics-empty-list">{t.clinics.dashboardEmpty}</div>
            ) : null}
          </div>
        </div>
      </section>

      <section className="rounded-[2rem] border border-border bg-white p-6 sm:p-8" data-testid="dashboard-history-section">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="font-heading text-2xl font-semibold text-slate-900" data-testid="dashboard-recent-title">{t.dashboard.recentTitle}</h3>
            <p className="mt-2 text-sm text-slate-600">{t.chat.historyHint}</p>
          </div>
        </div>

        <div className="mt-6 grid gap-4">
          {!loading && historyItems.length === 0 ? (
            <div className="rounded-[1.5rem] border border-dashed border-border bg-[#f8faf6] p-6 text-sm leading-7 text-slate-600" data-testid="dashboard-empty-state">{t.dashboard.empty}</div>
          ) : null}

          {historyItems.map((check) => (
            <article className={`rounded-[1.5rem] border p-5 ${check.severity === "High" ? "border-red-200 bg-red-50" : "border-border bg-[#fcfcfb]"}`} data-testid={`history-card-${check.id}`} key={check.id}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#8E9B86]">{new Date(check.created_at).toLocaleString()}</p>
                  <p className="mt-2 text-sm font-semibold text-slate-500" data-testid={`history-user-message-${check.id}`}>User: {check.message}</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900" data-testid={`history-ai-response-${check.id}`}>AI: {check.summary}</p>
                  {check.severity === "High" ? (
                    <div className="mt-3 grid gap-3">
                      <div className="rounded-xl border border-red-200 bg-red-100 px-3 py-2 text-sm font-semibold text-red-700" data-testid={`history-emergency-banner-${check.id}`}>{t.chat.emergencyBanner}</div>
                      <Button className="w-fit rounded-full bg-red-600 px-4 py-2 text-white hover:bg-red-700" data-testid={`history-sos-button-${check.id}`} onClick={triggerEmergency} type="button">
                        {t.chat.sosButton}
                      </Button>
                    </div>
                  ) : null}
                </div>
                <span className={`rounded-full px-3 py-1 text-sm font-semibold ${severityTone[check.severity]}`} data-testid={`history-severity-${check.id}`}>{getSeverityLabel(check.severity)}</span>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}