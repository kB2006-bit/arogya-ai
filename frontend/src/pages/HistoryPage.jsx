import { useState, useEffect } from "react";
import { Trash2, Calendar, AlertCircle, Info, Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAppContext } from "@/context/AppContext";
import { translations } from "@/lib/translations";
import { getSymptomHistory, clearSymptomHistory, deleteSymptomCheck } from "@/lib/symptomHistory";

const severityConfig = {
  High: { 
    bg: "bg-red-50", 
    text: "text-red-700", 
    border: "border-red-200",
    icon: "bg-red-100 text-red-600"
  },
  Medium: { 
    bg: "bg-amber-50", 
    text: "text-amber-700", 
    border: "border-amber-200",
    icon: "bg-amber-100 text-amber-600"
  },
  Low: { 
    bg: "bg-emerald-50", 
    text: "text-emerald-700", 
    border: "border-emerald-200",
    icon: "bg-emerald-100 text-emerald-600"
  }
};

export default function HistoryPage() {
  const { language } = useAppContext();
  const t = translations[language];
  const [history, setHistory] = useState([]);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  useEffect(() => {
    console.log('📜 Loading history...');
    loadHistory();
  }, []);

  const loadHistory = () => {
    const data = getSymptomHistory();
    console.log('📚 History loaded:', data.length, 'items');
    setHistory(data);
  };

  const handleClearHistory = () => {
    console.log('🗑️ Clearing all history...');
    if (clearSymptomHistory()) {
      console.log('✅ History cleared successfully');
      setHistory([]);
      setShowConfirmDialog(false);
    } else {
      console.error('❌ Failed to clear history');
    }
  };

  const handleDeleteItem = (id) => {
    console.log('🗑️ Deleting item:', id);
    if (deleteSymptomCheck(id)) {
      console.log('✅ Item deleted successfully');
      loadHistory();
    } else {
      console.error('❌ Failed to delete item');
    }
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString(language === 'hi' ? 'hi-IN' : 'en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.25em] text-slate-500">
              {language === 'hi' ? 'आपका स्वास्थ्य रिकॉर्ड' : 'Your Health Record'}
            </p>
            <h1 className="mt-3 font-heading text-3xl font-semibold text-slate-900">
              {language === 'hi' ? 'लक्षण इतिहास' : 'Symptom History'}
            </h1>
            <p className="mt-2 text-sm text-slate-600 max-w-2xl">
              {language === 'hi' 
                ? 'आपके पिछले सभी लक्षण मूल्यांकन यहां सहेजे गए हैं। अपने स्वास्थ्य की प्रगति को ट्रैक करें।'
                : 'All your previous symptom assessments are saved here. Track your health progress over time.'}
            </p>
          </div>
          {history.length > 0 && (
            <Button
              onClick={() => setShowConfirmDialog(true)}
              className="rounded-full bg-red-600 hover:bg-red-700 text-white px-6 py-3"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              {language === 'hi' ? 'इतिहास साफ करें' : 'Clear History'}
            </Button>
          )}
        </div>
      </div>

      {/* Confirm Dialog */}
      {showConfirmDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
                <AlertCircle className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                {language === 'hi' ? 'इतिहास साफ करें?' : 'Clear History?'}
              </h3>
            </div>
            <p className="text-sm text-slate-600 mb-6">
              {language === 'hi'
                ? 'यह क्रिया आपके सभी सहेजे गए लक्षण मूल्यांकन को स्थायी रूप से हटा देगी। यह पूर्ववत नहीं किया जा सकता।'
                : 'This will permanently delete all your saved symptom assessments. This action cannot be undone.'}
            </p>
            <div className="flex gap-3">
              <Button
                onClick={() => setShowConfirmDialog(false)}
                className="flex-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-900"
              >
                {language === 'hi' ? 'रद्द करें' : 'Cancel'}
              </Button>
              <Button
                onClick={handleClearHistory}
                className="flex-1 rounded-full bg-red-600 hover:bg-red-700 text-white"
              >
                {language === 'hi' ? 'हटाएं' : 'Delete'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* History Items */}
      {history.length === 0 ? (
        <div className="bg-white rounded-3xl border border-dashed border-slate-300 p-12 text-center">
          <div className="mx-auto w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
            <Heart className="h-8 w-8 text-slate-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            {language === 'hi' ? 'कोई इतिहास नहीं' : 'No History Yet'}
          </h3>
          <p className="text-sm text-slate-600">
            {language === 'hi'
              ? 'आपके लक्षण मूल्यांकन यहां दिखाई देंगे'
              : 'Your symptom assessments will appear here'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((item) => {
            const config = severityConfig[item.severity] || severityConfig.Low;
            return (
              <div
                key={item.id}
                className={`bg-white rounded-2xl border ${config.border} p-6 hover:shadow-md transition-all`}
              >
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`h-10 w-10 rounded-full ${config.icon} flex items-center justify-center shrink-0`}>
                      {item.severity === 'High' ? <AlertCircle className="h-5 w-5" /> : <Info className="h-5 w-5" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`inline-flex items-center rounded-full ${config.bg} px-3 py-1 text-xs font-semibold ${config.text}`}>
                          {item.severity} {language === 'hi' ? 'जोखिम' : 'Risk'}
                        </span>
                        <span className="text-xs text-slate-500 flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(item.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm font-medium text-slate-900 mb-1">
                        {item.diagnosis || item.message}
                      </p>
                      {item.summary && (
                        <p className="text-xs text-slate-600 line-clamp-2">
                          {item.summary}
                        </p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteItem(item.id)}
                    className="text-slate-400 hover:text-red-600 transition-colors p-2 rounded-full hover:bg-red-50"
                    title={language === 'hi' ? 'हटाएं' : 'Delete'}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>

                {item.next_steps && item.next_steps.length > 0 && (
                  <div className={`mt-3 rounded-xl ${config.bg} p-3`}>
                    <p className="text-xs font-semibold text-slate-700 mb-2">
                      {language === 'hi' ? 'अनुशंसित कार्रवाई:' : 'Recommended Action:'}
                    </p>
                    <p className="text-xs text-slate-600">
                      {item.next_steps[0]}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
