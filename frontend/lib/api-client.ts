// Determine API base URL:
// 1. Use NEXT_PUBLIC_API_URL environment variable if set (Vercel deployment)
// 2. Use localhost:8000 if running on localhost (local development)
// 3. Otherwise use deployed Render backend
const BASE_URL = (() => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  if (typeof window !== "undefined" && window.location.hostname === "localhost") {
    return "http://localhost:8000";
  }
  
  return "https://ai-voice-agent-l1x7.onrender.com";
})();

export interface RequestOptions extends RequestInit {
  json?: any;
  formData?: FormData;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.json) {
    headers.set("Content-Type", "application/json");
    options.body = JSON.stringify(options.json);
  } else if (options.formData) {
    // Note: Do NOT set Content-Type for FormData, the browser will set it with the correct boundary
    options.body = options.formData;
  }

  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorDetail = "An error occurred";
      try {
        const errorJson = await response.json();
        errorDetail = errorJson.detail || errorDetail;
      } catch {
        // Fallback if not JSON
      }
      throw new Error(errorDetail);
    }

    // Handle binary responses (e.g. downloads)
    const contentType = response.headers.get("content-type");
    if (contentType && (contentType.includes("application/pdf") || contentType.includes("text/csv") || contentType.includes("octet-stream"))) {
      return response as any;
    }

    return response.json();
  } catch (error: any) {
    // Improve error message for network errors
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error(`Failed to connect to server. Please check your internet connection and try again.`);
    }
    throw error;
  }
}

export const api = {
  // Auth
  login: (json: any) => request<any>("/api/v1/auth/login", { method: "POST", json }),
  signup: (json: any) => request<any>("/api/v1/auth/signup", { method: "POST", json }),
  me: () => request<any>("/api/v1/auth/me", { method: "GET" }),

  // Campaigns
  getCampaigns: () => request<any[]>("/api/v1/campaigns", { method: "GET" }),
  createCampaign: (json: any) => request<any>("/api/v1/campaigns", { method: "POST", json }),
  getCampaign: (id: number) => request<any>(`/api/v1/campaigns/${id}`, { method: "GET" }),
  updateCampaign: (id: number, json: any) => request<any>(`/api/v1/campaigns/${id}`, { method: "PUT", json }),
  deleteCampaign: (id: number) => request<any>(`/api/v1/campaigns/${id}`, { method: "DELETE" }),
  
  // Executions
  startCampaign: (id: number) => request<any>(`/api/v1/campaigns/${id}/start`, { method: "POST" }),
  pauseCampaign: (id: number) => request<any>(`/api/v1/campaigns/${id}/pause`, { method: "POST" }),
  resumeCampaign: (id: number) => request<any>(`/api/v1/campaigns/${id}/resume`, { method: "POST" }),
  stopCampaign: (id: number) => request<any>(`/api/v1/campaigns/${id}/stop`, { method: "POST" }),

  // Candidates
  getCandidates: (params?: { campaign_id?: number; search?: string; location?: string; skills?: string }) => {
    const q = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== "") {
          q.set(k, String(v));
        }
      });
    }
    const queryStr = q.toString() ? `?${q.toString()}` : "";
    return request<any[]>(`/api/v1/candidates${queryStr}`, { method: "GET" });
  },
  createCandidate: (json: any, campaignId?: number) => {
    const url = campaignId ? `/api/v1/candidates?campaign_id=${campaignId}` : "/api/v1/candidates";
    return request<any>(url, { method: "POST", json });
  },
  uploadCandidates: (formData: FormData) => {
    return request<any>("/api/v1/candidates/upload", { method: "POST", formData });
  },

  // Analytics
  getGlobalAnalytics: () => request<any>("/api/v1/analytics/global", { method: "GET" }),
  getCampaignAnalytics: (campaignId: number) => request<any>(`/api/v1/analytics/campaign/${campaignId}`, { method: "GET" }),
  getCampaignCandidatesUnified: (campaignId: number) => request<any[]>(`/api/v1/analytics/campaign/${campaignId}/candidates`, { method: "GET" }),

  // Notifications
  getNotifications: (unreadOnly = false) => request<any[]>(`/api/v1/notifications?unread_only=${unreadOnly}`, { method: "GET" }),
  markAllNotificationsRead: () => request<any>("/api/v1/notifications/read-all", { method: "PUT" }),
  markNotificationRead: (id: number) => request<any>(`/api/v1/notifications/${id}/read`, { method: "PUT" }),

  // Reports
  getReports: (campaignId: number) => request<any[]>(`/api/v1/reports/campaign/${campaignId}`, { method: "GET" }),
  generateReport: (campaignId: number, type: string, format: string) => {
    return request<any>(`/api/v1/reports/campaign/${campaignId}/generate?report_type=${type}&format=${format}`, { method: "POST" });
  },
  downloadReport: async (reportId: number, filename: string) => {
    const response = await request<Response>(`/api/v1/reports/download/${reportId}`, { method: "GET" });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
};
