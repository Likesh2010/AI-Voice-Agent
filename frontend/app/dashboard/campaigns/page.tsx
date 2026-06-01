"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../../lib/api-client";
import {
  Megaphone, Plus, Search, Calendar, MapPin, DollarSign,
  CircleDot, Play, Pause, Square, Trash2, ChevronRight
} from "lucide-react";

export default function CampaignsListPage() {
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const fetchCampaigns = async () => {
    try {
      const data = await api.getCampaigns();
      setCampaigns(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);
const handleCampaignAction = async (
  id: number,
  action: "start" | "pause" | "stop" | "resume"
) =>  {
    try {if (action === "start") {
  await api.startCampaign(id);
} else if (action === "resume") {
  await api.startCampaign(id);
} else if (action === "pause") {
  await api.pauseCampaign(id);
} else if (action === "stop") {
  await api.stopCampaign(id);
}
      fetchCampaigns();
    } catch (err: any) {
      alert(err.message || `Failed to ${action} campaign`);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this campaign? This cannot be undone.")) return;
    try {
      await api.deleteCampaign(id);
      setCampaigns(prev => prev.filter(c => c.id !== id));
    } catch (err: any) {
      alert(err.message || "Failed to delete campaign");
    }
  };

  // Filter campaigns
  const filteredCampaigns = campaigns.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.job_title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center text-slate-500 text-sm">
        <div className="flex flex-col items-center gap-2">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent"></div>
          <span>Syncing campaigns...</span>
        </div>
      </div>
    );
  }

  const tabs = ["all", "draft", "active", "paused", "stopped"];

  return (
    <div className="space-y-6 animate-in fade-in duration-200">

      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight">Campaigns</h1>
          <p className="text-sm text-slate-400">Launch and configure workflows for candidate evaluation</p>
        </div>
        <Link
          href="/dashboard/campaigns/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-900/30 transition-all active:scale-[0.98]"
        >
          <Plus className="w-4 h-4" />
          <span>New Campaign</span>
        </Link>
      </div>

      {/* FILTER BAR */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-slate-900/30 border border-slate-800 p-4 rounded-2xl">
        <div className="flex flex-wrap items-center gap-1.5 w-full md:w-auto">
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all ${statusFilter === tab
                  ? "bg-slate-800 border border-indigo-500/20 text-indigo-400"
                  : "text-slate-500 hover:text-slate-300"
                }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="relative w-full md:w-80">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search campaigns by name or title..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800/80 focus:border-indigo-500 text-slate-200 text-xs rounded-xl pl-10 pr-4 py-3 outline-none transition-all placeholder:text-slate-600"
          />
        </div>
      </div>

      {/* CAMPAIGNS GRID / CARDS */}
      {filteredCampaigns.length === 0 ? (
        <div className="bg-slate-900/10 border border-slate-800 border-dashed py-16 rounded-2xl text-center">
          <Megaphone className="w-10 h-10 text-slate-700 mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-400">No campaigns match your filters</p>
          <p className="text-xs text-slate-600 mt-1">Try tweaking your search or create a new campaign draft.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCampaigns.map((camp) => (
            <div
              key={camp.id}
              className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700/80 transition-all duration-200 hover:translate-y-[-2px] relative group"
            >
              {/* Campaign status indicator */}
              <div className="flex items-center justify-between mb-4">
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${camp.status === "active"
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

                {/* Delete button */}
                <button
                  onClick={() => handleDelete(camp.id)}
                  className="text-slate-600 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-950/20 transition-all opacity-0 group-hover:opacity-100 focus:opacity-100"
                  title="Delete Campaign"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Title & Details */}
              <div className="space-y-4 mb-6">
                <div>
                  <h3 className="text-lg font-bold text-slate-200 leading-tight truncate">
                    <Link href={`/dashboard/campaigns/${camp.id}`} className="hover:text-indigo-400 transition-colors">
                      {camp.name}
                    </Link>
                  </h3>
                  <p className="text-xs font-semibold text-slate-500 mt-0.5">{camp.job_title}</p>
                </div>

                <div className="space-y-2 text-xs text-slate-400">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span>{camp.location || "Remote"}</span>
                  </div>
                  {camp.salary_range && (
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                      <span>{camp.salary_range}</span>
                    </div>
                  )}
                  {camp.interview_date && (
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                      <span>
                        Interview: {new Date(camp.interview_date).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action buttons */}
              <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
                <Link
                  href={`/dashboard/campaigns/${camp.id}`}
                  className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 group-hover:translate-x-1 transition-transform"
                >
                  <span>Candidates</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>

                <div className="inline-flex gap-1.5">
                  {camp.status !== "active" ? (
                    <button
                      onClick={() => handleCampaignAction(camp.id, "start")}
                      className="p-1.5 rounded-lg border border-slate-800 hover:border-emerald-500/30 hover:bg-emerald-950/20 text-slate-400 hover:text-emerald-400 transition-all"
                      title="Launch"
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
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
}
