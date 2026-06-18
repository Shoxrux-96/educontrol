import { useState, useEffect } from "react";
import { Computer, ShieldCheck, Terminal, Monitor, Activity } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import type { DashboardStats, Computer as ComputerType } from "../types";
import { useAuth } from "../api/AuthContext";
import { StatCard } from "../components/Layout";

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [computers, setComputers] = useState<ComputerType[]>([]);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    api.get<DashboardStats>("/monitoring/dashboard").then((r) => setStats(r.data)).catch(() => {});
    api.get<{ items: ComputerType[] }>("/computers?page_size=5").then((r) => setComputers(r.data.items || [])).catch(() => {});
  }, []);

  const statusDot = (status: string) => {
    const colors: Record<string, string> = { online: "bg-emerald-500", offline: "bg-slate-300", busy: "bg-amber-500", locked: "bg-rose-500", maintenance: "bg-violet-500" };
    return colors[status] || "bg-slate-300";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Admin Dashboard</h1>
          <p className="text-sm text-slate-500">Xush kelibsiz, {user?.full_name || user?.username}</p>
        </div>
        <span className="px-3 py-1 bg-indigo-50 text-indigo-600 text-xs font-semibold rounded-full">Tashkilot admini</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Jami kompyuterlar" value={stats?.total_computers ?? 0} icon={Computer} color="indigo" />
        <StatCard title="Online" value={stats?.online_computers ?? 0} icon={Activity} color="emerald" />
        <StatCard title="Faol siyosatlar" value={stats?.active_policies ?? 0} icon={ShieldCheck} color="blue" />
        <StatCard title="Bugungi buyruqlar" value={stats?.commands_today ?? 0} icon={Terminal} color="amber" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-800">Oxirgi kompyuterlar</h2>
            <button onClick={() => navigate("/computers")} className="text-sm text-indigo-600 hover:text-indigo-700">Barchasi →</button>
          </div>
          <div className="space-y-2">
            {computers.map((c) => (
              <div key={c.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className={`w-2.5 h-2.5 rounded-full ${statusDot(c.status)}`} />
                  <div>
                    <p className="text-sm font-medium text-slate-700">{c.name}</p>
                    <p className="text-xs text-slate-400">{c.ip_address || c.hostname}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {c.cpu_usage !== undefined && (
                    <span className="text-xs text-slate-400">{c.cpu_usage}%</span>
                  )}
                  <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${c.status === "online" ? "bg-emerald-50 text-emerald-600" : "bg-slate-100 text-slate-400"}`}>
                    {c.status}
                  </span>
                </div>
              </div>
            ))}
            {computers.length === 0 && <p className="text-sm text-slate-400 text-center py-4">Kompyuter mavjud emas</p>}
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-500 to-blue-600 rounded-xl p-5 text-white">
          <h2 className="font-semibold mb-2">Tezkor amallar</h2>
          <p className="text-sm text-indigo-100 mb-4">Kompyuterlaringizni boshqaring</p>
          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => navigate("/computers")} className="flex items-center gap-2 bg-white/10 hover:bg-white/20 rounded-lg p-3 text-sm">
              <Monitor size={16} /> Kompyuterlar
            </button>
            <button onClick={() => navigate("/policies")} className="flex items-center gap-2 bg-white/10 hover:bg-white/20 rounded-lg p-3 text-sm">
              <ShieldCheck size={16} /> Siyosatlar
            </button>
            <button onClick={() => navigate("/commands")} className="flex items-center gap-2 bg-white/10 hover:bg-white/20 rounded-lg p-3 text-sm">
              <Terminal size={16} /> Buyruqlar
            </button>
            <button onClick={() => navigate("/monitoring")} className="flex items-center gap-2 bg-white/10 hover:bg-white/20 rounded-lg p-3 text-sm">
              <Activity size={16} /> Monitoring
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
