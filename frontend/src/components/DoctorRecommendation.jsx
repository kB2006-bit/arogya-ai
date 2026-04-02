import { Stethoscope, Brain, Heart, Activity, Baby, Eye, Ear } from "lucide-react";

const doctorRecommendations = {
  // Cardiac symptoms
  "chest pain": { type: "Cardiologist", icon: Heart, reason: "Specializes in heart and cardiovascular conditions" },
  "heart": { type: "Cardiologist", icon: Heart, reason: "Specializes in heart and cardiovascular conditions" },
  "cardiac": { type: "Cardiologist", icon: Heart, reason: "Specializes in heart and cardiovascular conditions" },
  
  // Neurological symptoms
  "headache": { type: "Neurologist", icon: Brain, reason: "Specializes in brain and nervous system disorders" },
  "migraine": { type: "Neurologist", icon: Brain, reason: "Specializes in brain and nervous system disorders" },
  "seizure": { type: "Neurologist", icon: Brain, reason: "Specializes in brain and nervous system disorders" },
  "stroke": { type: "Neurologist", icon: Brain, reason: "Specializes in brain and nervous system disorders" },
  "paralysis": { type: "Neurologist", icon: Brain, reason: "Specializes in brain and nervous system disorders" },
  
  // Dermatological symptoms
  "skin": { type: "Dermatologist", icon: Activity, reason: "Specializes in skin, hair, and nail conditions" },
  "rash": { type: "Dermatologist", icon: Activity, reason: "Specializes in skin, hair, and nail conditions" },
  "acne": { type: "Dermatologist", icon: Activity, reason: "Specializes in skin, hair, and nail conditions" },
  "eczema": { type: "Dermatologist", icon: Activity, reason: "Specializes in skin, hair, and nail conditions" },
  
  // Respiratory symptoms
  "breathing": { type: "Pulmonologist", icon: Activity, reason: "Specializes in respiratory and lung conditions" },
  "cough": { type: "Pulmonologist", icon: Activity, reason: "Specializes in respiratory and lung conditions" },
  "asthma": { type: "Pulmonologist", icon: Activity, reason: "Specializes in respiratory and lung conditions" },
  
  // Pediatric symptoms
  "child": { type: "Pediatrician", icon: Baby, reason: "Specializes in children's health and development" },
  "baby": { type: "Pediatrician", icon: Baby, reason: "Specializes in children's health and development" },
  "infant": { type: "Pediatrician", icon: Baby, reason: "Specializes in children's health and development" },
  
  // Eye symptoms
  "vision": { type: "Ophthalmologist", icon: Eye, reason: "Specializes in eye and vision conditions" },
  "eye": { type: "Ophthalmologist", icon: Eye, reason: "Specializes in eye and vision conditions" },
  "blind": { type: "Ophthalmologist", icon: Eye, reason: "Specializes in eye and vision conditions" },
  
  // Ear symptoms
  "ear": { type: "ENT Specialist", icon: Ear, reason: "Specializes in ear, nose, and throat conditions" },
  "hearing": { type: "ENT Specialist", icon: Ear, reason: "Specializes in ear, nose, and throat conditions" },
  "throat": { type: "ENT Specialist", icon: Ear, reason: "Specializes in ear, nose, and throat conditions" },
};

export function getDoctorRecommendation(message, diagnosis = "") {
  const searchText = `${message} ${diagnosis}`.toLowerCase();
  
  for (const [keyword, recommendation] of Object.entries(doctorRecommendations)) {
    if (searchText.includes(keyword)) {
      return recommendation;
    }
  }
  
  // Default recommendation
  return { 
    type: "General Physician", 
    icon: Stethoscope, 
    reason: "Can diagnose and treat a wide range of medical conditions" 
  };
}

export function DoctorRecommendationCard({ message, diagnosis }) {
  const recommendation = getDoctorRecommendation(message, diagnosis);
  const Icon = recommendation.icon;
  
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 hover-lift">
      <div className="flex items-start gap-4">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/30">
          <Icon className="h-7 w-7 text-white" />
        </div>
        <div className="flex-1">
          <p className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">
            Recommended Specialist
          </p>
          <h3 className="text-xl font-bold text-slate-900 mb-2">
            {recommendation.type}
          </h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            {recommendation.reason}
          </p>
        </div>
      </div>
    </div>
  );
}
