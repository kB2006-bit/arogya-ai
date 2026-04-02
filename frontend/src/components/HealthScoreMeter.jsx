import { AlertCircle, CheckCircle, AlertTriangle } from "lucide-react";

const severityConfig = {
  High: {
    color: "from-red-500 to-rose-600",
    bg: "bg-red-50",
    text: "text-red-700",
    icon: AlertCircle,
    label: "High Risk",
    message: "Requires immediate medical attention",
    score: 85,
  },
  Medium: {
    color: "from-amber-500 to-orange-600",
    bg: "bg-amber-50",
    text: "text-amber-700",
    icon: AlertTriangle,
    label: "Medium Risk",
    message: "Medical consultation recommended",
    score: 50,
  },
  Low: {
    color: "from-emerald-500 to-teal-600",
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    icon: CheckCircle,
    label: "Low Risk",
    message: "Monitor and self-care advised",
    score: 20,
  },
};

export function HealthScoreMeter({ severity }) {
  const config = severityConfig[severity] || severityConfig.Low;
  const Icon = config.icon;

  return (
    <div className={`rounded-2xl border border-slate-200 ${config.bg} p-6`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${config.color} shadow-lg`}>
            <Icon className="h-6 w-6 text-white" />
          </div>
          <div>
            <p className={`text-sm font-semibold ${config.text}`}>{config.label}</p>
            <p className="text-xs text-slate-600">{config.message}</p>
          </div>
        </div>
        <div className="text-right">
          <p className={`text-3xl font-bold ${config.text}`}>{config.score}</p>
          <p className="text-xs text-slate-500">Risk Score</p>
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="relative h-3 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${config.color} transition-all duration-1000 ease-out`}
          style={{ width: `${config.score}%` }}
        />
      </div>
      
      {/* Scale Labels */}
      <div className="mt-2 flex justify-between text-xs text-slate-500">
        <span>0</span>
        <span>50</span>
        <span>100</span>
      </div>
    </div>
  );
}
