import { useState, useEffect } from "react";
import { Computer, Monitor, Activity, History, BarChart3 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import type { DashboardStats } from "../types";
import { useAuth } from "../api/AuthContext";
import { StatCard } from "../components/Layout";

export default function ViewerDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    api.get<DashboardStats>("/monitoring/dashboard").then((r) => setStats(r.data)).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Kuzatuv paneli</h1>
          <p className="text-sm text-slate-500">Xush kelibsiz, {user?.full_name || user?.username}</p>
        </div>
        <span className="px-3 py-1 bg-slate-100 text-slate-600 text-xs font-semibold rounded-full">Kuzatuvchi</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Jami kompyuterlar" value={stats?.total_computers ?? 0} icon={Computer} color="indigo" />
        <StatCard title="Online" value={stats?.online_computers ?? 0} icon={Activity} color="emerald" />
        <StatCard title="Offline" value={stats?.offline_computers ?? 0} icon={Monitor} color="rose" />
        <StatCard title="Bugungi ogohlantirishlar" value={stats?.alerts_today ?? 0} icon={History} color="amber" />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <h2 className="font-semibold text-slate-800 mb-3">Ma'lumot</h2>
        <p className="text-sm text-slate-500">
          Siz <strong>kuzatuvchi</strong> sifatida tizimdagi kompyuterlar holatini, audit jurnalini va hisobotlarni 
          ko'rish huquqiga egasiz. O'zgartirish kiritish uchun admin bilan bog'laning.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button onClick={() => navigate("/computers")} className="bg-white rounded-xl border border-slate-200 p-5 text-left hover:shadow-md transition-shadow">
          <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center mb-3">
            <Computer size={20} className="text-indigo-600" />
          </div>
          <h3 className="font-semibold text-slate-800">Kompyuterlar</h3>
          <p className="text-sm text-slate-500 mt-1">Barcha kompyuterlar holatini ko'rish</p>
        </button>
        <button onClick={() => navigate("/audit")} className="bg-white rounded-xl border border-slate-200 p-5 text-left hover:shadow-md transition-shadow">
          <div className="w-10 h-10 bg-amber-50 rounded-xl flex items-center justify-center mb-3">
            <History size={20} className="text-amber-600" />
          </div>
          <h3 className="font-semibold text-slate-800">Audit jurnali</h3>
          <p className="text-sm text-slate-500 mt-1">Tizimdagi voqealar tarixini ko'rish</p>
        </button>
        <button onClick={() => navigate("/reports")} className="bg-white rounded-xl border border-slate-200 p-5 text-left hover:shadow-md transition-shadow">
          <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center mb-3">
            <BarChart3 size={20} className="text-emerald-600" />
          </div>
          <h3 className="font-semibold text-slate-800">Hisobotlar</h3>
          <p className="text-sm text-slate-500 mt-1">Hisobot va statistik ma'lumotlar</p>
        </button>
      </div>
    </div>
  );
}
