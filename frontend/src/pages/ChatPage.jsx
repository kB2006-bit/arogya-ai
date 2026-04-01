import { useMemo, useState } from "react";
import { AlertTriangle, Bot, SendHorizonal, Siren, UserRound } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAppContext } from "@/context/AppContext";
import { api, withAuth } from "@/lib/api";
import { translations } from "@/lib/translations";


const severityTone = {
  Low: "bg-[#e7f1e3] text-primary",
  Medium: "bg-[#fff2dd] text-[#b45309]",
  High: "bg-[#fee2e2] text-[#b91c1c]",
};


export default function ChatPage() {
  const { token, language } = useAppContext();
  const t = translations[language];
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [latestSeverity, setLatestSeverity] = useState("");
  const [messages, setMessages] = useState([
    {
      id: "welcome-message",
      role: "assistant",
      content: t.chat.assistantWelcome,
      result: null,
    },
  ]);

  const prompts = useMemo(() => t.chat.quickPrompts, [t]);

  const getSeverityLabel = (severity) => {
    if (severity === "Low") return t.common.severityLow;
    if (severity === "Medium") return t.common.severityMedium;
    return t.common.severityHigh;
  };

  const buildHistory = () =>
    messages
      .filter((item) => item.role === "user" || item.role === "assistant")
      .map((item) => ({ role: item.role, content: item.content }));

  const submitMessage = async (messageText) => {
    if (!messageText.trim()) {
      return;
    }

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: messageText.trim(),
      result: null,
    };

    setMessages((current) => [...current, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await api.post(
        "/symptom-checker",
        {
          message: messageText.trim(),
          language,
          history: [...buildHistory(), { role: "user", content: messageText.trim() }],
        },
        withAuth(token),
      );

      setLatestSeverity(response.data.severity);
      setMessages((current) => [
        ...current,
        {
          id: response.data.id,
          role: "assistant",
          content: response.data.summary,
          result: response.data,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: `assistant-error-${Date.now()}`,
          role: "assistant",
          content: language === "hi" ? "अभी जवाब देने में दिक्कत हो रही है। कृपया थोड़ी देर में फिर कोशिश करें।" : "I’m having trouble responding right now. Please try again in a moment.",
          result: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-6" data-testid="chat-page">
      {latestSeverity === "High" ? (
        <div className="animate-pulse rounded-[1.5rem] border border-red-200 bg-red-50 p-5 shadow-[0_0_20px_rgba(220,38,38,0.15)]" data-testid="high-severity-sos-card">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <Siren className="mt-1 h-6 w-6 text-red-600" />
              <div>
                <p className="font-semibold text-red-700">{t.chat.sos}</p>
                <p className="mt-1 text-sm text-red-600">{t.clinics.emergency}</p>
              </div>
            </div>
            <a className="rounded-full bg-red-600 px-5 py-3 text-sm font-semibold text-white" data-testid="chat-sos-call-button" href="tel:112">{t.chat.emergency}: 112</a>
          </div>
        </div>
      ) : null}

      <section className="rounded-[2rem] border border-border bg-white p-6 sm:p-8" data-testid="chat-main-section">
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-[#8E9B86]">ArogyaAI</p>
        <h2 className="mt-4 font-heading text-4xl font-semibold text-slate-900" data-testid="chat-title">{t.chat.title}</h2>
        <p className="mt-3 max-w-2xl text-base leading-8 text-slate-600" data-testid="chat-subtitle">{t.chat.subtitle}</p>
        <p className="mt-3 text-sm text-slate-500" data-testid="chat-history-hint">{t.chat.historyHint}</p>

        <div className="mt-6 flex flex-wrap gap-3">
          {prompts.map((prompt) => (
            <button className="rounded-full border border-border bg-[#f7f5ef] px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:border-primary hover:text-primary" data-testid={`chat-quick-prompt-${prompt.toLowerCase().replace(/\s+/g, "-")}`} key={prompt} onClick={() => setInput(prompt)} type="button">
              {prompt}
            </button>
          ))}
        </div>

        <div className="mt-6 rounded-[1.75rem] border border-border bg-[#f5f6f2] p-4 sm:p-5" data-testid="chat-thread-container">
          <div className="grid gap-4">
            {messages.map((message) => (
              <div className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`} data-testid={`chat-message-${message.id}`} key={message.id}>
                <div className={`max-w-[88%] rounded-[1.5rem] p-4 sm:max-w-[80%] ${message.role === "user" ? "rounded-tr-sm bg-primary text-white" : "rounded-tl-sm bg-white text-slate-900"}`}>
                  <div className="mb-3 flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] opacity-70">
                    {message.role === "user" ? <UserRound className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                    <span>{message.role === "user" ? t.chat.userLabel : t.chat.assistantLabel}</span>
                  </div>
                  <p className="text-sm leading-7 sm:text-base">{message.content}</p>

                  {message.result ? (
                    <div className="mt-4 grid gap-4 rounded-[1.25rem] border border-border/80 bg-[#f8faf6] p-4 text-slate-800" data-testid={`assistant-result-${message.id}`}>
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#8E9B86]">{t.chat.diagnosis}</p>
                          <p className="mt-1 font-semibold">{message.result.diagnosis}</p>
                        </div>
                        <span className={`rounded-full px-3 py-1 text-sm font-semibold ${severityTone[message.result.severity]}`} data-testid={`assistant-severity-${message.id}`}>
                          {t.chat.severity}: {getSeverityLabel(message.result.severity)}
                        </span>
                      </div>

                      <div>
                        <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#8E9B86]">{t.chat.nextSteps}</p>
                        <ul className="mt-2 grid gap-2 text-sm leading-7">
                          {message.result.next_steps.map((step) => <li key={step}>• {step}</li>)}
                        </ul>
                      </div>

                      <div>
                        <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#8E9B86]">{t.chat.warningSigns}</p>
                        <ul className="mt-2 grid gap-2 text-sm leading-7 text-slate-600">
                          {message.result.warning_signs.map((sign) => <li key={sign}>• {sign}</li>)}
                        </ul>
                      </div>

                      <div className="rounded-[1rem] border border-red-200 bg-red-50 p-3 text-sm text-red-700" data-testid={`assistant-emergency-${message.id}`}>
                        <div className="flex items-start gap-2">
                          <AlertTriangle className="mt-1 h-4 w-4 shrink-0" />
                          <span>{message.result.emergency_message}</span>
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-[1.5rem] border border-border bg-white p-3 sm:p-4" data-testid="chat-input-panel">
            <Textarea className="min-h-[120px] resize-none rounded-[1.25rem] border-0 bg-[#f5f6f2] px-5 py-4 text-base shadow-none focus-visible:ring-2 focus-visible:ring-[#8E9B86]" data-testid="chat-message-input" onChange={(event) => setInput(event.target.value)} placeholder={t.chat.placeholder} value={input} />
            <div className="mt-3 flex justify-end">
              <Button className="rounded-full bg-primary px-5 py-6 text-white hover:bg-primary/90" data-testid="chat-submit-button" disabled={loading || !input.trim()} onClick={() => submitMessage(input)} type="button">
                <SendHorizonal className="h-4 w-4" />
                {loading ? t.common.loading : t.chat.send}
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}