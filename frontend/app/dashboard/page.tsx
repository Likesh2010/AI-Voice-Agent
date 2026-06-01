"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../lib/api-client";
import { 
  Megaphone, Users, PhoneCall, MessageSquare, Plus, ArrowRight,
  TrendingUp, CircleDot, Play, Pause, Square
} from "lucide-react";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>({
    total_campaigns: 0,
    active_campaigns: 0,
    total_candidates: 0,
    avg_voice_interest: 0,
    avg_whatsapp_engagement: 0,
    recent_activity: []
  });
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      const statsData = await api.getGlobalAnalytics();
      setStats(statsData);
      
      const campaignsList = await api.getCampaigns();
      setCampaigns(campaignsList);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleCampaignAction = async (id: number, action: "start" | "pause" | "stop" | "resume") => {
    try {
      if (action === "start") await api.startCampaign(id);
      else if (action === "resume") await api.resumeCampaign(id);
      else if (action === "pause") await api.pauseCampaign(id);
      else if (action === "stop") await api.stopCampaign(id);
      fetchDashboardData();
    } catch (err: any) {
      alert(err.message || `Failed to ${action} campaign`);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center text-slate-500 text-sm">
        <div className="flex flex-col items-center gap-2">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent"></div>
          <span>Loading overview...</span>
        </div>
      </div>
    );
  }

  // Calculate status counts for mock chart
  const statusValues = [65, 78, 52, 85, 90, 72, 80];

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      
      {/* HEADER SECTION */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight">Overview</h1>
          <p className="text-sm text-slate-400">Recruitment campaigns orchestration & response metrics</p>
        </div>
        <Link 
          href="/dashboard/campaigns/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-900/30 transition-all hover:translate-y-[-1px] active:translate-y-0"
        >
          <Plus className="w-4 h-4" />
          <span>New Campaign</span>
        </Link>
      </div>

      {/* METRICS CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Total Campaigns */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 rounded-full bg-indigo-500/5 blur-2xl pointer-events-none group-hover:scale-125 transition-transform duration-300"></div>
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Campaigns</span>
            <div className="h-8 w-8 rounded-lg bg-indigo-950/60 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Megaphone className="w-4 h-4" />
            </div>
          </div>
          <div className="space-y-1">
            <h3 className="text-3xl font-extrabold text-slate-100">{stats.total_campaigns}</h3>
            <p className="text-xs text-slate-500 font-medium">
              <span className="text-indigo-400">{stats.active_campaigns} active</span> campaign executions
            </p>
          </div>
        </div>

        {/* Total Candidates */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 rounded-full bg-emerald-500/5 blur-2xl pointer-events-none group-hover:scale-125 transition-transform duration-300"></div>
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Candidates Contacted</span>
            <div className="h-8 w-8 rounded-lg bg-emerald-950/60 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="space-y-1">
            <h3 className="text-3xl font-extrabold text-slate-100">{stats.total_candidates}</h3>
            <p className="text-xs text-slate-500 font-medium">Total sync database matches</p>
          </div>
        </div>

        {/* Voice Interest */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 rounded-full bg-violet-500/5 blur-2xl pointer-events-none group-hover:scale-125 transition-transform duration-300"></div>
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Voice Avg Interest</span>
            <div className="h-8 w-8 rounded-lg bg-violet-950/60 border border-violet-500/20 text-violet-400 flex items-center justify-center">
              <PhoneCall className="w-4 h-4" />
            </div>
          </div>
          <div className="space-y-1">
            <h3 className="text-3xl font-extrabold text-slate-100">
              {stats.avg_voice_interest > 0 ? `${stats.avg_voice_interest}%` : "N/A"}
            </h3>
            <p className="text-xs text-slate-500 font-medium">Calculated from voice agent calls</p>
          </div>
        </div>

        {/* WhatsApp Engagement */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 rounded-full bg-fuchsia-500/5 blur-2xl pointer-events-none group-hover:scale-125 transition-transform duration-300"></div>
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">WhatsApp Engagement</span>
            <div className="h-8 w-8 rounded-lg bg-fuchsia-950/60 border border-fuchsia-500/20 text-fuchsia-400 flex items-center justify-center">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="space-y-1">
            <h3 className="text-3xl font-extrabold text-slate-100">
              {stats.avg_whatsapp_engagement > 0 ? `${stats.avg_whatsapp_engagement}%` : "N/A"}
            </h3>
            <p className="text-xs text-slate-500 font-medium">Calculated from chat replies</p>
          </div>
        </div>

      </div>

      {/* CHARTS & RECENT ACTIVITY LAYOUT */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Custom SVG Trend Chart */}
        <div className="lg:col-span-2 bg-slate-900/30 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-100">Orchestrator Activity</h3>
              <p className="text-xs text-slate-500">Average combined candidate evaluation response trends</p>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 bg-slate-800/50 border border-slate-700 rounded-lg text-xs font-semibold text-slate-400">
              <TrendingUp className="w-3.5 h-3.5 text-indigo-400" /> +8.3% this week
            </div>
          </div>

          {/* Area Line Chart using raw SVG */}
          <div className="h-64 relative w-full pt-4">
            <svg viewBox="0 0 700 240" className="w-full h-full text-indigo-500" preserveAspectRatio="none">
              <defs>
                <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4f46e5" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#4f46e5" stopOpacity="0" />
                </linearGradient>
              </defs>
              
              {/* Grid Lines */}
              <line x1="0" y1="40" x2="700" y2="40" stroke="#1e293b" strokeWidth="1" strokeDasharray="4" />
              <line x1="0" y1="100" x2="700" y2="100" stroke="#1e293b" strokeWidth="1" strokeDasharray="4" />
              <line x1="0" y1="160" x2="700" y2="160" stroke="#1e293b" strokeWidth="1" strokeDasharray="4" />
              <line x1="0" y1="220" x2="700" y2="220" stroke="#1e293b" strokeWidth="1" />

              {/* Area Path */}
              <path 
                d={`M 0,220 L 0,${220 - statusValues[0]*1.8} L 116,${220 - statusValues[1]*1.8} L 233,${220 - statusValues[2]*1.8} L 350,${220 - statusValues[3]*1.8} L 466,${220 - statusValues[4]*1.8} L 583,${220 - statusValues[5]*1.8} L 700,${220 - statusValues[6]*1.8} L 700,220 Z`}
                fill="url(#chartGrad)"
              />
              
              {/* Line Path */}
              <path 
                d={`M 0,${220 - statusValues[0]*1.8} L 116,${220 - statusValues[1]*1.8} L 233,${220 - statusValues[2]*1.8} L 350,${220 - statusValues[3]*1.8} L 466,${220 - statusValues[4]*1.8} L 583,${220 - statusValues[5]*1.8} L 700,${220 - statusValues[6]*1.8}`}
                fill="none"
                stroke="#6366f1"
                strokeWidth="3.5"
                strokeLinecap="round"
              />

              {/* Nodes dots */}
              {[0, 116, 233, 350, 466, 583, 700].map((x, idx) => (
                <circle 
                  key={x}
                  cx={x}
                  cy={220 - statusValues[idx]*1.8}
                  r="5"
                  className="fill-indigo-500 stroke-slate-950 stroke-2 hover:r-7 hover:fill-fuchsia-400 cursor-pointer transition-all"
                />
              ))}
            </svg>

            {/* Labels overlay */}
            <div className="flex justify-between text-[10px] text-slate-500 font-semibold pt-2 px-1">
              <span>Mon</span>
              <span>Tue</span>
              <span>Wed</span>
              <span>Thu</span>
              <span>Fri</span>
              <span>Sat</span>
              <span>Sun</span>
            </div>
          </div>
        </div>

        {/* Recent Activity List */}
        <div className="bg-slate-900/30 border border-slate-800 rounded-2xl p-6 space-y-4 flex flex-col h-full">
          <div>
            <h3 className="text-lg font-bold text-slate-100">Live Feed</h3>
            <p className="text-xs text-slate-500">Real-time candidate agent callbacks</p>
          </div>
          
          <div className="flex-1 space-y-3.5 overflow-y-auto max-h-[260px] pr-1">
            {stats.recent_activity.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-12">No candidate executions triggered yet.</p>
            ) : (
              stats.recent_activity.map((act: any, idx: number) => (
                <div key={idx} className="flex gap-3 text-xs leading-5 p-3 rounded-xl bg-slate-900/40 border border-slate-800/50">
                  <div className={`h-7 w-7 shrink-0 rounded-full flex items-center justify-center ${
                    act.type === "voice" 
                      ? "bg-violet-950 text-violet-400 border border-violet-500/20" 
                      : "bg-fuchsia-950 text-fuchsia-400 border border-fuchsia-500/20"
                  }`}>
                    {act.type === "voice" ? <PhoneCall className="w-3.5 h-3.5" /> : <MessageSquare className="w-3.5 h-3.5" />}
                  </div>
                  <div className="flex-1 space-y-0.5">
                    <p className="text-slate-300 font-semibold leading-none">
                      {act.candidate_name}{" "}
                      <span className="text-[10px] font-normal text-slate-500">in {act.campaign_name}</span>
                    </p>
                    <p className="text-[11px] text-slate-400 font-medium line-clamp-1">{act.summary}</p>
                    <div className="flex items-center justify-between text-[10px] text-slate-500 pt-0.5">
                      <span>Score: <b className="text-slate-300">{act.score}</b></span>
                      <span>
                        {new Date(act.time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

      {/* CAMPAIGN LIST GRID */}
      <div className="bg-slate-900/30 border border-slate-800 rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-100">Recruitment Campaigns</h3>
            <p className="text-xs text-slate-500">Configure parameters, link candidates and execute flows</p>
          </div>
          <Link 
            href="/dashboard/campaigns"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            <span>View All Campaigns</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Campaigns Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px] font-bold">
                <th className="pb-3 pl-4">Campaign Name</th>
                <th className="pb-3">Target Role</th>
                <th className="pb-3">Location</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 pr-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {campaigns.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500">
                    No campaigns created yet. Click &quot;New Campaign&quot; to begin.
                  </td>
                </tr>
              ) : (
                campaigns.slice(0, 5).map((camp) => (
                  <tr key={camp.id} className="hover:bg-slate-900/20 transition-colors group">
                    <td className="py-3.5 pl-4">
                      <Link 
                        href={`/dashboard/campaigns/${camp.id}`} 
                        className="font-bold text-slate-200 hover:text-indigo-400 transition-colors"
                      >
                        {camp.name}
                      </Link>
                    </td>
                    <td className="py-3.5 text-slate-300 font-semibold">{camp.job_title}</td>
                    <td className="py-3.5 text-slate-400">{camp.location || "Remote"}</td>
                    <td className="py-3.5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        camp.status === "active" 
                          ? "bg-emerald-950/40 text-emerald-400 border border-emerald-500/20" 
                          : camp.status === "paused"
                          ? "bg-amber-950/40 text-amber-400 border border-amber-500/20"
                          : camp.status === "stopped"
                          ? "bg-rose-950/40 text-rose-400 border border-rose-500/20"
                          : "bg-slate-800/40 text-slate-400 border border-slate-700/50"
                      }`}>
                        <CircleDot className="w-2 h-2 fill-current" />
                        {camp.status}
                      </span>
                    </td>
                    <td className="py-3.5 pr-4 text-right">
                      <div className="inline-flex gap-1.5 justify-end">
                        {camp.status !== "active" ? (
                          <button
                            onClick={() => handleCampaignAction(camp.id, camp.status === "paused" ? "resume" : "start")}
                            className="p-1.5 rounded-lg border border-slate-800 hover:border-emerald-500/30 hover:bg-emerald-950/20 text-slate-400 hover:text-emerald-400 transition-all"
                            title="Start/Resume"
                          >
                            <Play className="w-3.5 h-3.5 fill-current" />
                          </button>
                        ) : (
                          <button
                            onClick={() => handleCampaignAction(camp.id, "pause")}
                            className="p-1.5 rounded-lg border border-slate-800 hover:border-amber-500/30 hover:bg-amber-950/20 text-slate-400 hover:text-amber-400 transition-all"
                            title="Pause"
                          >
                            <Pause className="w-3.5 h-3.5 fill-current" />
                          </button>
                        )}
                        {(camp.status === "active" || camp.status === "paused") && (
                          <button
                            onClick={() => handleCampaignAction(camp.id, "stop")}
                            className="p-1.5 rounded-lg border border-slate-800 hover:border-rose-500/30 hover:bg-rose-950/20 text-slate-400 hover:text-rose-400 transition-all"
                            title="Stop"
                          >
                            <Square className="w-3.5 h-3.5 fill-current" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
