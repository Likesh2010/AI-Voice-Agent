"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../../../lib/api-client";
import { 
  Building, Calendar, DollarSign, MapPin, Shield, ChevronRight, 
  ChevronLeft, PhoneCall, MessageSquare, Plus, Trash2, Save 
} from "lucide-react";

export default function NewCampaignPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Step 1: Campaign Details
  const [name, setName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [experienceRequired, setExperienceRequired] = useState("");
  const [salaryRange, setSalaryRange] = useState("");
  const [location, setLocation] = useState("");
  const [interviewDate, setInterviewDate] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");

  // Step 2: Agent Configurations
  // Voice
  const [voiceSchedule, setVoiceSchedule] = useState("Weekdays 9 AM - 5 PM EST");
  const [voiceQuestions, setVoiceQuestions] = useState<string[]>([
    "Explain React Server Components and their advantages.",
    "Describe a challenging project you built recently and how you resolved technical obstacles."
  ]);
  const [newVoiceQuestion, setNewVoiceQuestion] = useState("");
  const [voiceParams, setVoiceParams] = useState<string[]>(["Technical accuracy", "Communication clarity", "Tone & Confidence"]);
  const [newVoiceParam, setNewVoiceParam] = useState("");

  // WhatsApp
  const [waTemplate, setWaTemplate] = useState("Hi {{name}}, are you interested in our new React Developer opportunity?");
  const [waQuestions, setWaQuestions] = useState<string[]>([
    "What is your earliest availability for an interview?",
    "Confirm your current location and salary expectations."
  ]);
  const [newWaQuestion, setNewWaQuestion] = useState("");
  const [waParams, setWaParams] = useState<string[]>(["Response speed", "Engagement depth", "Notice matching"]);
  const [newWaParam, setNewWaParam] = useState("");

  const handleAddVoiceQuestion = () => {
    if (newVoiceQuestion.trim()) {
      setVoiceQuestions([...voiceQuestions, newVoiceQuestion.trim()]);
      setNewVoiceQuestion("");
    }
  };

  const handleAddVoiceParam = () => {
    if (newVoiceParam.trim()) {
      setVoiceParams([...voiceParams, newVoiceParam.trim()]);
      setNewVoiceParam("");
    }
  };

  const handleAddWaQuestion = () => {
    if (newWaQuestion.trim()) {
      setWaQuestions([...waQuestions, newWaQuestion.trim()]);
      setNewWaQuestion("");
    }
  };

  const handleAddWaParam = () => {
    if (newWaParam.trim()) {
      setWaParams([...waParams, newWaParam.trim()]);
      setNewWaParam("");
    }
  };

  const handleSubmit = async () => {
    setError("");
    setLoading(true);

    const payload = {
      name,
      job_title: jobTitle,
      job_description: jobDescription,
      required_skills: requiredSkills,
      experience_required: experienceRequired,
      salary_range: salaryRange,
      location,
      interview_date: interviewDate ? new Date(interviewDate).toISOString() : null,
      additional_notes: additionalNotes,
      voice_config: {
        questions: voiceQuestions,
        evaluation_parameters: voiceParams,
        calling_schedule: voiceSchedule
      },
      whatsapp_config: {
        message_templates: waTemplate,
        questions: waQuestions,
        evaluation_parameters: waParams
      }
    };

    try {
      await api.createCampaign(payload);
      router.push("/dashboard/campaigns");
    } catch (err: any) {
      setError(err.message || "Failed to create campaign");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in duration-200">
      
      {/* HEADER */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight">Create Campaign</h1>
        <p className="text-sm text-slate-400">Configure parameters for automated candidate evaluations</p>
      </div>

      {/* STEP GRAPHIC */}
      <div className="flex items-center justify-center gap-6 py-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold ${
            step === 1 ? "bg-indigo-600 text-white" : "bg-slate-800 text-slate-400"
          }`}>
            1
          </span>
          <span className={`text-xs font-semibold ${step === 1 ? "text-indigo-400" : "text-slate-500"}`}>
            Job details
          </span>
        </div>
        <ChevronRight className="w-4 h-4 text-slate-700" />
        <div className="flex items-center gap-2">
          <span className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold ${
            step === 2 ? "bg-indigo-600 text-white" : "bg-slate-800 text-slate-400"
          }`}>
            2
          </span>
          <span className={`text-xs font-semibold ${step === 2 ? "text-indigo-400" : "text-slate-500"}`}>
            Configure Agents
          </span>
        </div>
      </div>

      {error && (
        <div className="flex gap-2 p-3.5 rounded-xl border border-red-500/20 bg-red-950/20 text-red-400 text-xs">
          <Shield className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* FORM STEPS */}
      <div className="bg-slate-900/30 border border-slate-800 rounded-2xl p-8 shadow-xl">
        
        {/* STEP 1: JOB DETAILS */}
        {step === 1 && (
          <div className="space-y-6">
            <h3 className="text-base font-bold text-slate-200">Step 1: Campaign & Role Details</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Campaign Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. React Developer Q3 Hiring"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Target Job Title
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Senior Frontend Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Required Experience
                </label>
                <input
                  type="text"
                  placeholder="e.g. 5+ years"
                  value={experienceRequired}
                  onChange={(e) => setExperienceRequired(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Salary Range
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3.5 top-3.5 w-3.5 h-3.5 text-slate-500" />
                  <input
                    type="text"
                    placeholder="e.g. $120,000 - $140,000"
                    value={salaryRange}
                    onChange={(e) => setSalaryRange(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl pl-9 pr-4 py-3 outline-none transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Location
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3.5 top-3.5 w-3.5 h-3.5 text-slate-500" />
                  <input
                    type="text"
                    placeholder="e.g. Remote (US/Canada)"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl pl-9 pr-4 py-3 outline-none transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Interview Date
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3.5 top-3.5 w-3.5 h-3.5 text-slate-500" />
                  <input
                    type="datetime-local"
                    value={interviewDate}
                    onChange={(e) => setInterviewDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl pl-9 pr-4 py-3 outline-none transition-all"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                Required Technical Skills (Comma separated)
              </label>
              <input
                type="text"
                placeholder="React, TypeScript, Next.js, CSS, Tailwind"
                value={requiredSkills}
                onChange={(e) => setRequiredSkills(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none transition-all"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                Job Description
              </label>
              <textarea
                rows={4}
                placeholder="Describe role responsibilities, team structures, and project scopes..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none transition-all resize-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                Additional Notes
              </label>
              <input
                type="text"
                placeholder="Notes visible only to you"
                value={additionalNotes}
                onChange={(e) => setAdditionalNotes(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none transition-all"
              />
            </div>

            <div className="flex justify-end pt-4">
              <button
                type="button"
                onClick={() => {
                  if (!name || !jobTitle) {
                    setError("Campaign Name and Target Job Title are required.");
                  } else {
                    setError("");
                    setStep(2);
                  }
                }}
                className="inline-flex items-center gap-1.5 px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all"
              >
                <span>Continue Configurations</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: AGENT CONFIGURATIONS */}
        {step === 2 && (
          <div className="space-y-8">
            
            {/* VOICE AGENT SETTINGS */}
            <div className="space-y-5 border-b border-slate-800/80 pb-6">
              <div className="flex items-center gap-2 text-indigo-400">
                <PhoneCall className="w-5 h-5" />
                <h3 className="text-base font-bold text-slate-200">Voice Screening Agent Configuration</h3>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Calling Schedule Limit
                </label>
                <input
                  type="text"
                  value={voiceSchedule}
                  onChange={(e) => setVoiceSchedule(e.target.value)}
                  placeholder="e.g. Weekdays 9 AM - 5 PM EST"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none transition-all"
                />
              </div>

              {/* Questions list */}
              <div className="space-y-3">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
                  Screening Questions List
                </label>
                <div className="space-y-2">
                  {voiceQuestions.map((q, idx) => (
                    <div key={idx} className="flex gap-2 items-center bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-xs text-slate-300">
                      <span className="text-slate-500 font-bold shrink-0">{idx + 1}.</span>
                      <p className="flex-1">{q}</p>
                      <button 
                        type="button" 
                        onClick={() => setVoiceQuestions(voiceQuestions.filter((_, i) => i !== idx))}
                        className="text-slate-500 hover:text-red-400"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newVoiceQuestion}
                    onChange={(e) => setNewVoiceQuestion(e.target.value)}
                    placeholder="Add screening question..."
                    className="flex-1 bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-2.5 outline-none transition-all"
                  />
                  <button
                    type="button"
                    onClick={handleAddVoiceQuestion}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Eval parameters */}
              <div className="space-y-3">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
                  Evaluation Criteria Parameters
                </label>
                <div className="flex flex-wrap gap-2">
                  {voiceParams.map((p, idx) => (
                    <span key={idx} className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-950/40 border border-indigo-500/20 text-indigo-400 text-xs font-medium">
                      <span>{p}</span>
                      <button 
                        type="button" 
                        onClick={() => setVoiceParams(voiceParams.filter((_, i) => i !== idx))}
                        className="text-indigo-400/60 hover:text-red-400"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2 max-w-sm">
                  <input
                    type="text"
                    value={newVoiceParam}
                    onChange={(e) => setNewVoiceParam(e.target.value)}
                    placeholder="e.g. Technical depth"
                    className="flex-1 bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-2.5 outline-none transition-all"
                  />
                  <button
                    type="button"
                    onClick={handleAddVoiceParam}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* WHATSAPP AGENT SETTINGS */}
            <div className="space-y-5">
              <div className="flex items-center gap-2 text-fuchsia-400">
                <MessageSquare className="w-5 h-5" />
                <h3 className="text-base font-bold text-slate-200">WhatsApp Chat Agent Configuration</h3>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Initial Greeting Message Template
                </label>
                <textarea
                  rows={2}
                  value={waTemplate}
                  onChange={(e) => setWaTemplate(e.target.value)}
                  placeholder="Hi {{name}}, are you open for a quick chat?"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-3 outline-none transition-all resize-none"
                />
              </div>

              {/* Questions list */}
              <div className="space-y-3">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
                  WhatsApp Conversation Prompt List
                </label>
                <div className="space-y-2">
                  {waQuestions.map((q, idx) => (
                    <div key={idx} className="flex gap-2 items-center bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-xs text-slate-300">
                      <span className="text-slate-500 font-bold shrink-0">{idx + 1}.</span>
                      <p className="flex-1">{q}</p>
                      <button 
                        type="button" 
                        onClick={() => setWaQuestions(waQuestions.filter((_, i) => i !== idx))}
                        className="text-slate-500 hover:text-red-400"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newWaQuestion}
                    onChange={(e) => setNewWaQuestion(e.target.value)}
                    placeholder="Add prompt question..."
                    className="flex-1 bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-2.5 outline-none transition-all"
                  />
                  <button
                    type="button"
                    onClick={handleAddWaQuestion}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Eval parameters */}
              <div className="space-y-3">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">
                  Evaluation Criteria Parameters
                </label>
                <div className="flex flex-wrap gap-2">
                  {waParams.map((p, idx) => (
                    <span key={idx} className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-fuchsia-950/40 border border-fuchsia-500/20 text-fuchsia-400 text-xs font-medium">
                      <span>{p}</span>
                      <button 
                        type="button" 
                        onClick={() => setWaParams(waParams.filter((_, i) => i !== idx))}
                        className="text-fuchsia-400/60 hover:text-red-400"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2 max-w-sm">
                  <input
                    type="text"
                    value={newWaParam}
                    onChange={(e) => setNewWaParam(e.target.value)}
                    placeholder="e.g. Availability fit"
                    className="flex-1 bg-slate-950 border border-slate-800 focus:border-indigo-500 text-slate-200 text-xs rounded-xl px-4 py-2.5 outline-none transition-all"
                  />
                  <button
                    type="button"
                    onClick={handleAddWaParam}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Navigation controls */}
            <div className="flex justify-between items-center pt-6 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="inline-flex items-center gap-1 px-4 py-2.5 rounded-xl border border-slate-800 hover:bg-slate-850 hover:text-slate-200 text-slate-400 text-xs font-bold"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Job Details</span>
              </button>
              
              <button
                type="button"
                onClick={handleSubmit}
                disabled={loading}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-900/20 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>Create Campaign Draft</span>
                  </>
                )}
              </button>
            </div>

          </div>
        )}

      </div>

    </div>
  );
}
