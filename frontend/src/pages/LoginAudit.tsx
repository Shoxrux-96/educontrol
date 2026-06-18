import { useState, useEffect, useCallback } from "react";
import { LogIn, Shield, AlertTriangle, Search, Clock, UserX, UserCheck } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface LoginRecord {
  id: string;
  username: string;
  ip_address: string;
  hostname?: string;
  result: "success" | "failed" | "locked" | "timeout";
  failure_reason?: string;
  user_agent?: string;
  session_duration?: number;
  logged_at: string;
}

interface LoginSummary {
  total: number;
  success: number;
  failed: number;
  locked: number;
}

const resultStyles: Record<string, string> = {
  success: "bg-emerald-100 text-emerald-700",
  failed: "bg-rose-100 text-rose-700",
  locked: "bg-amber-100 text-amber-700",
  timeout: "bg-slate-100 text-slate-600",
};

function fmtDuration(seconds?: number): string {
  if (seconds == null) return "—";
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m}m`;
}

export default function LoginAudit() {
  const [records, setRecords] = useState<LoginRecord[]>([]);
  const [summary, setSummary] = useState<LoginSummary | null>(null);
  const [username, setUsername] = useState("");
  const [resultFilter, setResultFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const { isAdmin } = useAuth();

  const fetchSummary = useCallback(() => {
    api.get<LoginSummary>("/security/logins/summary").then((r) => setSummary(r.data)).catch(() => {});
  }, []);

  const fetchRecords = useCallback(() => {
    const params = new URLSearchParams();
    if (username) params.set("username", username);
    if (resultFilter) params.set("result", resultFilter);
    params.set("limit", "200");
    api.get<{ items: LoginRecord[] }>(`/security/logins?${params}`)
      .then((r) => setRecords(r.data.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [username, resultFilter]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  useEffect(() => {
    setLoading(true);
    fetchRecords();
  }, [fetchRecords]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchRecords();
      fetchSummary();
    }, 30000);
    return () => clearInterval(interval);
  }, [fetchRecords, fetchSummary]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Login auditi</h1>
        {isAdmin && (
          <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors">
            <span>Eksport</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4">
          <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
            <LogIn size={20} className="text-indigo-600" />
          </div>
          <div>
            <p className="text-xs text-slate-400">Jami loginlar</p>
            <p className="text-xl font-bold text-slate-800">{summary?.total ?? "—"}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4">
          <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
            <UserCheck size={20} className="text-emerald-600" />
          </div>
          <div>
            <p className="text-xs text-slate-400">Muvaffaqiyatli</p>
            <p className="text-xl font-bold text-slate-800">{summary?.success ?? "—"}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4">
          <div className="w-10 h-10 bg-rose-100 rounded-xl flex items-center justify-center">
            <UserX size={20} className="text-rose-600" />
          </div>
          <div>
            <p className="text-xs text-slate-400">Muvaffaqiyatsiz</p>
            <p className="text-xl font-bold text-slate-800">{summary?.failed ?? "—"}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4">
          <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
            <Shield size={20} className="text-amber-600" />
          </div>
          <div>
            <p className="text-xs text-slate-400">Bloklangan</p>
            <p className="text-xl font-bold text-slate-800">{summary?.locked ?? "—"}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text" value={username} onChange={(e) => setUsername(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Username bo'yicha qidirish..."
            />
          </div>
          <select
            value={resultFilter} onChange={(e) => setResultFilter(e.target.value)}
            className="px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Barcha natijalar</option>
            <option value="success">Muvaffaqiyatli</option>
            <option value="failed">Muvaffaqiyatsiz</option>
            <option value="locked">Bloklangan</option>
          </select>
          <button
            onClick={() => { fetchRecords(); fetchSummary(); }}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
          >
            <Clock size={16} /> Yangilash
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Username</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">IP manzil</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Hostname</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Natija</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Sabab</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">User Agent</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Sessiya</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Vaqt</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map((r) => (
                <tr
                  key={r.id}
                  className={`hover:bg-slate-50 ${r.result === "failed" ? "border-l-2 border-l-rose-500" : ""}`}
                >
                  <td className="px-4 py-3 font-medium text-slate-700">{r.username}</td>
                  <td className="px-4 py-3 text-slate-500 font-mono text-xs">{r.ip_address}</td>
                  <td className="px-4 py-3 text-slate-500">{r.hostname || "—"}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${resultStyles[r.result] || "bg-slate-100 text-slate-600"}`}>
                      {r.result === "failed" && <AlertTriangle size={12} />}
                      {r.result}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500 max-w-[120px] truncate" title={r.failure_reason}>
                    {r.failure_reason || "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-xs max-w-[160px] truncate" title={r.user_agent}>
                    {r.user_agent || "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{fmtDuration(r.session_duration)}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs whitespace-nowrap">
                    {new Date(r.logged_at).toLocaleString("uz-UZ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {loading && (
          <div className="text-center py-8 text-slate-400">
            <div className="animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-2" />
            Yuklanmoqda...
          </div>
        )}
        {!loading && records.length === 0 && (
          <div className="text-center py-12 text-slate-400">Login yozuvlari topilmadi</div>
        )}
      </div>
    </div>
  );
}
