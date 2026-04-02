import { HeartPulse, Loader2 } from "lucide-react";

export function LoadingAnalysis({ message = "Analyzing your symptoms..." }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8">
      <div className="flex flex-col items-center justify-center text-center space-y-4">
        <div className="relative">
          {/* Pulsing background */}
          <div className="absolute inset-0 rounded-full bg-emerald-500/20 animate-ping" />
          
          {/* Icon container */}
          <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/30">
            <HeartPulse className="h-8 w-8 text-white animate-pulse" />
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-emerald-600" />
            <p className="text-base font-semibold text-slate-900">
              {message}
            </p>
          </div>
          <p className="text-sm text-slate-600">
            Our AI is carefully analyzing your symptoms
          </p>
        </div>

        {/* Progress dots */}
        <div className="flex gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: "0ms" }} />
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: "150ms" }} />
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  );
}
