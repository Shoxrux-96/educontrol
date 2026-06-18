import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Wifi, WifiOff, Monitor, MonitorSmartphone, Power, Package, PowerOff, RotateCcw, Moon } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";
import type { Computer } from "../types";

export default function ComputersPage() {
  const [computers, setComputers] = useState<Computer[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState<string | null>(null);
  const { isAdmin } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    api.get<{ items: Computer[] }>("/computers").then((r) => setComputers(r.data.items || [])).catch(() => {});
  }, []);

  const filtered = computers.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.ip_address?.includes(search)
  );

  const statusBadge = (status: string) => {
    const m: Record<string, string> = { online: "bg-emerald-100 text-emerald-700", offline: "bg-slate-100 text-slate-500", busy: "bg-amber-100 text-amber-700", locked: "bg-rose-100 text-rose-700", maintenance: "bg-violet-100 text-violet-700" };
    return m[status] || "bg-slate-100 text-slate-500";
  };

  const handlePower = async (computerId: string, action: string) => {
    setLoading(`${computerId}-${action}`);
    try {
      await api.post(`/computers/${computerId}/power`, { action });
    } catch (e) {
      console.error(e);
    }
    setLoading(null);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Kompyuterlar</h1>
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Qidirish..."
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((c) => (
          <div key={c.id} className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center">
                  <Monitor size={20} className="text-slate-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800">{c.name}</h3>
                  <p className="text-xs text-slate-400">{c.ip_address || c.hostname}</p>
                </div>
              </div>
              {c.status === "online" ? <Wifi size={18} className="text-emerald-500" /> : <WifiOff size={18} className="text-slate-300" />}
            </div>
            <div className="flex flex-wrap gap-2 text-xs mb-3">
              <span className={`px-2 py-1 rounded-full font-medium ${statusBadge(c.status)}`}>
                {c.status}
              </span>
              {c.os_version && <span className="px-2 py-1 bg-slate-100 rounded-full text-slate-600">{c.os_version}</span>}
              {c.agent_version && <span className="px-2 py-1 bg-slate-100 rounded-full text-slate-600">v{c.agent_version}</span>}
            </div>
            {c.cpu_usage !== undefined && (
              <div className="mb-3 space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-500 w-8">CPU</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-1.5">
                    <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${c.cpu_usage}%` }} />
                  </div>
                  <span className="text-slate-600 w-8 text-right">{c.cpu_usage}%</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-500 w-8">RAM</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-1.5">
                    <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${c.ram_usage}%` }} />
                  </div>
                  <span className="text-slate-600 w-8 text-right">{c.ram_usage}%</span>
                </div>
              </div>
            )}
            {isAdmin && (
              <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-slate-100">
                <button
                  onClick={() => navigate(`/remote-desktop/${c.id}`)}
                  className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors"
                  title="Remote Desktop"
                >
                  <MonitorSmartphone size={14} /> RD
                </button>
                <button
                  onClick={() => navigate(`/software/${c.id}`)}
                  className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                  title="Dasturlar"
                >
                  <Package size={14} /> Dastur
                </button>
                <button
                  onClick={() => handlePower(c.id, "shutdown")}
                  disabled={loading === `${c.id}-shutdown`}
                  className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-rose-50 text-rose-600 rounded-lg hover:bg-rose-100 transition-colors disabled:opacity-50"
                  title="O'chirish"
                >
                  <PowerOff size={14} />
                </button>
                <button
                  onClick={() => handlePower(c.id, "restart")}
                  disabled={loading === `${c.id}-restart`}
                  className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-amber-50 text-amber-600 rounded-lg hover:bg-amber-100 transition-colors disabled:opacity-50"
                  title="Qayta ishga tushirish"
                >
                  <RotateCcw size={14} />
                </button>
                <button
                  onClick={() => handlePower(c.id, "sleep")}
                  disabled={loading === `${c.id}-sleep`}
                  className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
                  title="Uyqu rejimi"
                >
                  <Moon size={14} />
                </button>
                <button
                  onClick={() => handlePower(c.id, "wake")}
                  disabled={loading === `${c.id}-wake`}
                  className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors disabled:opacity-50"
                  title="Wake on LAN"
                >
                  <Power size={14} />
                </button>
              </div>
            )}
            <p className="text-xs text-slate-400 mt-3">
              Oxirgi ko'rinish: {c.last_seen ? new Date(c.last_seen).toLocaleString("uz-UZ") : "Noma'lum"}
            </p>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="col-span-full text-center py-12 text-slate-400">Kompyuter topilmadi</div>
        )}
      </div>
    </div>
  );
}
