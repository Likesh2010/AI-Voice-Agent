"use client";

import { ReactNode, useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "../../hooks/use-auth";
import { api } from "../../lib/api-client";
import { 
  LayoutDashboard, Megaphone, Users, BarChart3, FileText, 
  LogOut, Bell, Menu, X, User as UserIcon, Building
} from "lucide-react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);

  // Fetch alerts
  const fetchAlerts = async () => {
    if (!user) return;
    try {
      const data = await api.getNotifications();
      setNotifications(data);
    } catch {
      // Ignored
    }
  };

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user) {
      fetchAlerts();
      const interval = setInterval(fetchAlerts, 20000); // refresh every 20s
      return () => clearInterval(interval);
    }
  }, [user]);

  const handleMarkRead = async (id: number) => {
    try {
      await api.markNotificationRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
    } catch {
      // Ignored
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    } catch {
      // Ignored
    }
  };

  if (loading || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent"></div>
          <p className="text-sm font-medium tracking-wide">Syncing Session...</p>
        </div>
      </div>
    );
  }

  const unreadCount = notifications.filter(n => !n.read).length;

  const menuItems = [
    { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
    { label: "Campaigns", href: "/dashboard/campaigns", icon: Megaphone },
    { label: "Candidate DB", href: "/dashboard/candidates", icon: Users },
    { label: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
    { label: "Reports", href: "/dashboard/reports", icon: FileText },
  ];

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden font-sans">
      
      {/* SIDEBAR - Desktop */}
      <aside className="hidden md:flex md:flex-shrink-0 md:w-64 bg-slate-900 border-r border-slate-800 flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-800">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-fuchsia-500 flex items-center justify-center font-bold text-white text-base">
              R
            </div>
            <span className="font-bold text-lg text-slate-100 tracking-tight">RecruitAgent</span>
          </Link>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {menuItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.label}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-150 ${
                  isActive 
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-900/20" 
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                }`}
              >
                <item.icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* User profile footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-3 px-2 py-1 mb-3">
            <div className="h-9 w-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 font-semibold">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-semibold text-slate-200 truncate">{user.name}</p>
              <p className="text-xs text-slate-500 truncate flex items-center gap-1">
                <Building className="w-3 h-3 inline" /> {user.company || "No company"}
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center gap-2.5 px-4 py-2.5 rounded-xl text-xs font-semibold text-red-400 hover:bg-red-950/20 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out Session</span>
          </button>
        </div>
      </aside>

      {/* MOBILE SIDEBAR MODAL */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 md:hidden flex">
          <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm" onClick={() => setSidebarOpen(false)}></div>
          <div className="relative flex flex-col w-72 bg-slate-900 border-r border-slate-800 z-50">
            <div className="h-16 flex items-center justify-between px-6 border-b border-slate-800">
              <Link href="/dashboard" className="flex items-center gap-2" onClick={() => setSidebarOpen(false)}>
                <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white">R</div>
                <span className="font-bold text-lg text-slate-100">RecruitAgent</span>
              </Link>
              <button onClick={() => setSidebarOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>
            <nav className="flex-1 px-4 py-6 space-y-1">
              {menuItems.map((item) => (
                <Link
                  key={item.label}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium ${
                    pathname === item.href ? "bg-indigo-600 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              ))}
            </nav>
            <div className="p-4 border-t border-slate-800 bg-slate-900/50">
              <button
                onClick={() => { logout(); setSidebarOpen(false); }}
                className="w-full flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold text-red-400 hover:bg-red-950/20"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out Session</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MAIN CONTAINER */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        
        {/* NAVBAR */}
        <header className="h-16 border-b border-slate-800 bg-slate-900/30 backdrop-blur-md flex items-center justify-between px-6 z-20">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(true)} className="md:hidden text-slate-400 hover:text-slate-200">
              <Menu className="w-5 h-5" />
            </button>
            <h2 className="text-base font-semibold text-slate-200 capitalize">
              {pathname === "/dashboard" ? "Dashboard Summary" : pathname.split("/").pop()}
            </h2>
          </div>

          <div className="flex items-center gap-4 relative">
            {/* NOTIFICATIONS CONTAINER */}
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-full border border-slate-800 hover:border-slate-700 bg-slate-900/50 text-slate-400 hover:text-slate-200 transition-all outline-none"
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 h-5 w-5 bg-indigo-500 rounded-full flex items-center justify-center text-[10px] font-bold text-white border-2 border-slate-900 animate-pulse">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notification Drawer Popover */}
            {showNotifications && (
              <>
                <div className="fixed inset-0 z-30" onClick={() => setShowNotifications(false)}></div>
                <div className="absolute right-0 top-12 w-80 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-4 space-y-3 z-40 max-h-96 overflow-y-auto">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Alert Center</span>
                    {unreadCount > 0 && (
                      <button 
                        onClick={handleMarkAllRead} 
                        className="text-[10px] font-semibold text-indigo-400 hover:underline"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>
                  <div className="space-y-2">
                    {notifications.length === 0 ? (
                      <p className="text-xs text-slate-500 text-center py-4">No recent notifications</p>
                    ) : (
                      notifications.map((n) => (
                        <div 
                          key={n.id} 
                          onClick={() => !n.read && handleMarkRead(n.id)}
                          className={`p-2.5 rounded-xl border text-xs cursor-pointer transition-colors ${
                            n.read 
                              ? "bg-slate-900/30 border-slate-800/40 text-slate-500" 
                              : "bg-slate-800/40 border-indigo-500/20 text-slate-300 hover:bg-slate-800/60"
                          }`}
                        >
                          <div className="flex justify-between font-semibold mb-1 text-[11px]">
                            <span className={n.read ? "text-slate-400" : "text-indigo-400"}>{n.title}</span>
                            <span className="text-slate-500 font-normal">
                              {new Date(n.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </span>
                          </div>
                          <p className="leading-4">{n.message}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </header>

        {/* SCREEN CONTENT */}
        <main className="flex-1 overflow-y-auto bg-slate-950 p-6 md:p-8">
          {children}
        </main>
      </div>

    </div>
  );
}
