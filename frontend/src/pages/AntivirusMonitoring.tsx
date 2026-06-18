import { useState, useEffect } from "react";
import { Shield, ShieldCheck, ShieldOff, AlertTriangle, Bug, Search, CheckCircle, XCircle, RefreshCw } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface AntivirusStatus {
  id: string;
  computer_id: string;
  computer_name: string;
  product: string;
  version: string;
  definitions_version: string;
  definitions_up_to_date: boolean;
  realtime_protection: boolean;
  firewall_enabled: boolean;
  last_scan: string;
  threats_found: number;
  status: string;
}

interface AntivirusSummary {
  protected: number;
  unprotected: number;
  outdated_definitions: number;
  realtime_off: number;
  requires_restart: number;
}

interface Threat {
  id: string;
  threat_type: string;
  severity: string;
  computer_name: string;
  file_path: string;
  detected_by: string;
  detected_at: string;
  status: string;
}

interface ThreatStats {
  virus: number;
  trojan: number;
  miner: number;
  ransomware: number;
  spyware: number;
  other: number;
}

const severityColors: Record<string, string> = {
  critical: "bg-rose-100 text-rose-700",
  high: "bg-amber-100 text-amber-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-slate-100 text-slate-600",
};

const statusColors: Record<string, string> = {
  running: "bg-emerald-100 text-emerald-700",
  stopped: "bg-rose-100 text-rose-700",
  "not installed": "bg-slate-100 text-slate-500",
};

const threatIcons: Record<string, typeof Bug> = {
  virus: Bug,
  trojan: Bug,
  miner: Bug,
  ransomware: Bug,
  spyware: Bug,
};

export default function AntivirusMonitoring() {
  const [summary, setSummary] = useState<AntivirusSummary | null>(null);
  const [antivirusList, setAntivirusList] = useState<AntivirusStatus[]>([]);
  const [threats, setThreats] = useState<Threat[]>([]);
  const [stats, setStats] = useState<ThreatStats | null>(null);
  const [severityFilter, setSeverityFilter] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState<string | null>(null);
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [s, a, t, st] = await Promise.all([
        api.get<AntivirusSummary>("/security/antivirus/summary"),
        api.get<AntivirusStatus[]>("/security/antivirus"),
        api.get<Threat[]>("/security/threats", { params: { severity: severityFilter || undefined, limit: 100 } }),
        api.get<ThreatStats>("/security/threats/stats"),
      ]);
      setSummary(s.data);
      setAntivirusList(a.data);
      setThreats(t.data);
      setStats(st.data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  useEffect(() => {
    api.get<Threat[]>("/security/threats", { params: { severity: severityFilter || undefined, limit: 100 } })
      .then((r) => setThreats(r.data))
      .catch(() => {});
  }, [severityFilter]);

  const handleResolve = async (id: string) => {
    setResolving(id);
    try {
      await api.patch(`/security/threats/${id}/resolve`);
      setThreats((prev) => prev.map((t) => (t.id === id ? { ...t, status: "cleaned" } : t)));
    } catch { /* ignore */ }
    setResolving(null);
  };

  const filtered = antivirusList.filter((a) =>
    a.computer_name.toLowerCase().includes(search.toLowerCase()) ||
    a.product?.toLowerCase().includes(search.toLowerCase())
  );

  const ThreatIcon = (type: string) => {
    const Icon = threatIcons[type] || Bug;
    return <Icon size={16} className="text-slate-500" />;
  };

  const card = (label: string, value: number, icon: React.ReactNode, bg: string, text: string) => (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-slate-500 font-medium">{label}</span>
        {icon}
      </div>
      <p className={`text-2xl font-bold ${text}`}>{value}</p>
    </div>
  );

  if (loading) {
    return <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">Antivirus monitoringi</h1>
        <button onClick={fetchAll} className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">
          <RefreshCw size={14} /> Yangilash
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {card("Himoyalangan", summary?.protected ?? 0, <ShieldCheck size={18} className="text-emerald-500" />, "bg-emerald-50", "text-emerald-700")}
        {card("Himoyasiz", summary?.unprotected ?? 0, <ShieldOff size={18} className="text-rose-500" />, "bg-rose-50", "text-rose-700")}
        {card("Eskirgan definitsiyalar", summary?.outdated_definitions ?? 0, <AlertTriangle size={18} className="text-amber-500" />, "bg-amber-50", "text-amber-700")}
        {card("Realtime o'chiq", summary?.realtime_off ?? 0, <XCircle size={18} className="text-orange-500" />, "bg-orange-50", "text-orange-700")}
        {card("Qayta ishga tushirish", summary?.requires_restart ?? 0, <RefreshCw size={18} className="text-blue-500" />, "bg-blue-50", "text-blue-700")}
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="font-semibold text-slate-800">Antivirus holati</h2>
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Qidirish..."
            />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 text-xs uppercase tracking-wider border-b border-slate-100">
                <th className="text-left px-5 py-3 font-medium">Kompyuter</th>
                <th className="text-left px-5 py-3 font-medium">Mahsulot</th>
                <th className="text-left px-5 py-3 font-medium">Versiya</th>
                <th className="text-left px-5 py-3 font-medium">Definitsiyalar</th>
                <th className="text-center px-5 py-3 font-medium">Realtime</th>
                <th className="text-center px-5 py-3 font-medium">Firewall</th>
                <th className="text-left px-5 py-3 font-medium">Oxirgi skaner</th>
                <th className="text-right px-5 py-3 font-medium">Tahdidlar</th>
                <th className="text-center px-5 py-3 font-medium">Holat</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((a) => (
                <tr key={a.id} className="text-slate-700 hover:bg-slate-50">
                  <td className="px-5 py-3 font-medium">{a.computer_name}</td>
                  <td className="px-5 py-3">{a.product}</td>
                  <td className="px-5 py-3 text-slate-500">{a.version}</td>
                  <td className="px-5 py-3">
                    <span className="text-slate-600">{a.definitions_version}</span>
                    {a.definitions_up_to_date ? (
                      <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-emerald-100 text-emerald-700">
                        <CheckCircle size={10} /> Yangi
                      </span>
                    ) : (
                      <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-amber-100 text-amber-700">
                        <AlertTriangle size={10} /> Eski
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-center">
                    {a.realtime_protection ? (
                      <span className="inline-flex items-center gap-1 text-emerald-600"><ShieldCheck size={14} /> Yoqilgan</span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-rose-600"><ShieldOff size={14} /> O'chiq</span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-center">
                    {a.firewall_enabled ? (
                      <span className="inline-flex items-center gap-1 text-emerald-600"><CheckCircle size={14} /> Yoqilgan</span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-rose-600"><XCircle size={14} /> O'chiq</span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-slate-500">
                    {a.last_scan ? new Date(a.last_scan).toLocaleString("uz-UZ") : "Noma'lum"}
                  </td>
                  <td className="px-5 py-3 text-right font-semibold">{a.threats_found}</td>
                  <td className="px-5 py-3 text-center">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusColors[a.status] || "bg-slate-100 text-slate-500"}`}>
                      {a.status}
                    </span>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={9} className="text-center py-12 text-slate-400">Ma'lumot mavjud emas</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200">
          <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
            <h2 className="font-semibold text-slate-800">Tahdidlar</h2>
            <div className="flex items-center gap-3">
              <select
                value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}
                className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Barchasi</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-slate-500 text-xs uppercase tracking-wider border-b border-slate-100">
                  <th className="text-left px-5 py-3 font-medium">Tur</th>
                  <th className="text-left px-5 py-3 font-medium">Daraja</th>
                  <th className="text-left px-5 py-3 font-medium">Kompyuter</th>
                  <th className="text-left px-5 py-3 font-medium">Fayl</th>
                  <th className="text-left px-5 py-3 font-medium">Aniqlagan</th>
                  <th className="text-left px-5 py-3 font-medium">Aniqlangan vaqt</th>
                  <th className="text-center px-5 py-3 font-medium">Holat</th>
                  {isAdmin && <th className="text-center px-5 py-3 font-medium"></th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {threats.map((t) => (
                  <tr key={t.id} className="text-slate-700 hover:bg-slate-50">
                    <td className="px-5 py-3">
                      <span className="inline-flex items-center gap-1.5">
                        {ThreatIcon(t.threat_type)} {t.threat_type}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${severityColors[t.severity] || "bg-slate-100 text-slate-500"}`}>
                        {t.severity}
                      </span>
                    </td>
                    <td className="px-5 py-3">{t.computer_name}</td>
                    <td className="px-5 py-3 text-slate-500 max-w-[200px] truncate" title={t.file_path}>{t.file_path}</td>
                    <td className="px-5 py-3">{t.detected_by}</td>
                    <td className="px-5 py-3 text-slate-500 whitespace-nowrap">
                      {t.detected_at ? new Date(t.detected_at).toLocaleString("uz-UZ") : ""}
                    </td>
                    <td className="px-5 py-3 text-center">
                      {t.status === "quarantined" ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                          <AlertTriangle size={10} /> Karantin
                        </span>
                      ) : t.status === "cleaned" ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                          <CheckCircle size={10} /> Tozalangan
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-rose-100 text-rose-700">
                          <XCircle size={10} /> Yechilmagan
                        </span>
                      )}
                    </td>
                    {isAdmin && t.status === "unresolved" && (
                      <td className="px-5 py-3 text-center">
                        <button
                          onClick={() => handleResolve(t.id)}
                          disabled={resolving === t.id}
                          className="px-3 py-1.5 text-xs font-medium bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 disabled:opacity-50 transition-colors"
                        >
                          {resolving === t.id ? "..." : "Yechish"}
                        </button>
                      </td>
                    )}
                    {isAdmin && t.status !== "unresolved" && (
                      <td className="px-5 py-3 text-center text-slate-300">-</td>
                    )}
                  </tr>
                ))}
                {threats.length === 0 && (
                  <tr><td colSpan={isAdmin ? 8 : 7} className="text-center py-12 text-slate-400">Tahdidlar mavjud emas</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200">
          <div className="px-5 py-4 border-b border-slate-200">
            <h2 className="font-semibold text-slate-800">Tahdid statistikasi</h2>
          </div>
          <div className="p-5 space-y-4">
            {stats && (
              Object.entries(stats).map(([key, value]) => {
                const total = Object.values(stats).reduce((a, b) => a + b, 0) || 1;
                const pct = Math.round((value / total) * 100);
                const barColors: Record<string, string> = {
                  virus: "bg-rose-500",
                  trojan: "bg-amber-500",
                  miner: "bg-yellow-500",
                  ransomware: "bg-red-600",
                  spyware: "bg-violet-500",
                  other: "bg-slate-400",
                };
                return (
                  <div key={key}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-700 font-medium capitalize">{key}</span>
                      <span className="text-slate-500">{value} ({pct}%)</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div className={`h-2 rounded-full ${barColors[key] || "bg-slate-400"}`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })
            )}
            {(!stats || Object.values(stats).every((v) => v === 0)) && (
              <p className="text-center py-6 text-slate-400">Statistika mavjud emas</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
