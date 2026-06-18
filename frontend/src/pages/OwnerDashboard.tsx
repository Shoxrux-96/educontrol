import { useState, useEffect } from "react";
import { Building2, Monitor, ShieldCheck, Activity, Globe, Plus, TrendingUp } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import type { DashboardStats, Organization } from "../types";
import { useAuth } from "../api/AuthContext";
import { StatCard } from "../components/Layout";

export default function OwnerDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    api.get<DashboardStats>("/monitoring/dashboard").then((r) => setStats(r.data)).catch(() => {});
    api.get<Organization[]>("/organizations").then((r) => setOrgs(r.data)).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Owner Dashboard</h1>
          <p className="text-sm text-slate-500">Xush kelibsiz, {user?.full_name || user?.username}</p>
        </div>
        <span className="px-3 py-1 bg-violet-50 text-violet-600 text-xs font-semibold rounded-full">Tizim egasi</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Tashkilotlar" value={orgs.length} icon={Building2} color="violet" />
        <StatCard title="Jami kompyuterlar" value={stats?.total_computers ?? 0} icon={Monitor} color="indigo" />
        <StatCard title="Online" value={stats?.online_computers ?? 0} icon={Activity} color="emerald" />
        <StatCard title="Faol siyosatlar" value={stats?.active_policies ?? 0} icon={ShieldCheck} color="blue" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h2 className="font-semibold text-slate-800 mb-4">Tashkilotlar</h2>
          <div className="space-y-3">
            {orgs.slice(0, 5).map((org) => (
              <div key={org.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Globe size={18} className="text-slate-500" />
                  <div>
                    <p className="text-sm font-medium text-slate-700">{org.name}</p>
                    <p className="text-xs text-slate-400">{org.user_count ?? 0} foydalanuvchi</p>
                  </div>
                </div>
                <span className={`px-2 py-0.5 text-xs rounded-full ${org.is_active ? "bg-emerald-50 text-emerald-600" : "bg-slate-100 text-slate-400"}`}>
                  {org.is_active ? "Faol" : "Blok"}
                </span>
              </div>
            ))}
            {orgs.length === 0 && <p className="text-sm text-slate-400 text-center py-4">Tashkilot mavjud emas</p>}
          </div>
          <button onClick={() => navigate("/organizations")} className="mt-4 text-sm text-indigo-600 hover:text-indigo-700 font-medium">
            Barcha tashkilotlar →
          </button>
        </div>

        <div className="bg-gradient-to-br from-indigo-500 to-blue-600 rounded-xl p-5 text-white">
          <h2 className="font-semibold mb-2">Tezkor amallar</h2>
          <p className="text-sm text-indigo-100 mb-4">Tashkilot va foydalanuvchilarni boshqaring</p>
          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => navigate("/organizations")} className="flex items-center gap-2 bg-white/10 hover:bg-white/20 rounded-lg p-3 text-sm">
              <Plus size={16} /> Yangi tashkilot
            </button>
            <button onClick={() => navigate("/settings")} className="flex items-center gap-2 bg-white/10 hover:bg-white/20 rounded-lg p-3 text-sm">
              <TrendingUp size={16} /> Tizim sozlamalari
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
