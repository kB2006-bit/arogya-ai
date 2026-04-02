import { AlertTriangle, CheckCircle2, Info, ArrowRight } from "lucide-react";
import { HealthScoreMeter } from "./HealthScoreMeter";
import { DoctorRecommendationCard } from "./DoctorRecommendation";

export function SymptomResultCard({ result, message }) {
  const getSeverityIcon = (severity) => {
    switch (severity) {
      case "High":
        return <AlertTriangle className="h-5 w-5" />;
      case "Medium":
        return <Info className="h-5 w-5" />;
      default:
        return <CheckCircle2 className="h-5 w-5" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "High":
        return "border-red-200 bg-red-50";
      case "Medium":
        return "border-amber-200 bg-amber-50";
      default:
        return "border-emerald-200 bg-emerald-50";
    }
  };

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Health Score Meter */}
      <HealthScoreMeter severity={result.severity} />

      {/* Diagnosis Card */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <div className="flex items-start gap-3 mb-4">
          <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${getSeverityColor(result.severity)}`}>
            {getSeverityIcon(result.severity)}
          </div>
          <div className="flex-1">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
              Assessment Result
            </p>
            <h3 className="text-lg font-bold text-slate-900">
              {result.diagnosis}
            </h3>
          </div>
        </div>
        
        <p className="text-sm text-slate-700 leading-relaxed mb-4">
          {result.summary}
        </p>

        {result.emergency_message && result.severity === "High" && (
          <div className="rounded-xl bg-red-100 border border-red-200 p-4 mb-4">
            <p className="text-sm font-semibold text-red-900">
              {result.emergency_message}
            </p>
          </div>
        )}
      </div>

      {/* Doctor Recommendation */}
      <DoctorRecommendationCard message={message} diagnosis={result.diagnosis} />

      {/* Next Steps */}
      {result.next_steps && result.next_steps.length > 0 && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6">
          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4">
            Recommended Actions
          </h4>
          <div className="space-y-3">
            {result.next_steps.map((step, index) => (
              <div key={index} className="flex items-start gap-3">
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 text-xs font-bold mt-0.5">
                  {index + 1}
                </div>
                <p className="text-sm text-slate-700 leading-relaxed flex-1">
                  {step}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warning Signs */}
      {result.warning_signs && result.warning_signs.length > 0 && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <h4 className="text-sm font-bold text-amber-900">
              Watch for These Warning Signs
            </h4>
          </div>
          <ul className="space-y-2">
            {result.warning_signs.map((sign, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-amber-800">
                <ArrowRight className="h-4 w-4 mt-0.5 shrink-0" />
                <span>{sign}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
