import { useState, useEffect, useRef } from "react";
import { Terminal, AlertTriangle, AlertCircle, Info, Search, Filter, RefreshCw, Server } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface SyslogEntry {
  id: string;
  timestamp: string;
  hostname: string;
  ip: string;
  facility: string;
  severity: string;
  app_name: string;
  message: string;
  raw_log?: string;
}

interface SyslogSummary {
  total: number;
  critical_emergency: number;
  errors: number;
  warnings: number;
}

interface HostSummary {
  hostname: string;
  log_count: number;
  last_seen: string;
}

const SEVERITIES = ["", "emergency", "alert", "critical", "error", "warning", "notice", "info", "debug"];

const severityColor: Record<string, string> = {
  emergency: "bg-rose-100 text-rose-700",
  alert: "bg-rose-100 text-rose-700",
  critical: "bg-rose-100 text-rose-700",
  error: "bg-amber-100 text-amber-700",
  warning: "bg-yellow-100 text-yellow-700",
  notice: "bg-blue-100 text-blue-700",
  info: "bg-slate-100 text-slate-700",
  debug: "bg-gray-100 text-gray-700",
};

export default function SyslogServer() {
  const [entries, setEntries] = useState<SyslogEntry[]>([]);
  const [summary, setSummary] = useState<SyslogSummary | null>(null);
  const [hosts, setHosts] = useState<HostSummary[]>([]);
  const [hostnames, setHostnames] = useState<string[]>([]);
  const [hostname, setHostname] = useState("");
  const [severity, setSeverity] = useState("");
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchData();
    intervalRef.current = setInterval(fetchData, 15000);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, []);

  useEffect(() => {
    api.get<string[]>("/enterprise/syslog/hosts").then((r) => setHostnames(r.data)).catch(() => {});
  }, []);

  const fetchData = async () => {
    try {
      const params: Record<string, string> = { limit: "200" };
      if (hostname) params.hostname = hostname;
      if (severity) params.severity = severity;
      if (search) params.search = search;
      const [e, s, h] = await Promise.all([
        api.get<SyslogEntry[]>("/enterprise/syslog", { params }),
        api.get<SyslogSummary>("/enterprise/syslog/summary"),
        api.get<HostSummary[]>("/enterprise/syslog/hosts"),
      ]);
      setEntries(e.data);
      setSummary(s.data);
      setHosts(h.data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const handleFilter = () => {
    setLoading(true);
    fetchData();
  };

  if (loading && entries.length === 0) {
    return <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">Syslog Viewer</h1>
        <button onClick={handleFilter} className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">
          <RefreshCw size={14} /> Yangilash
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
              <Terminal size={20} className="text-indigo-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">{summary?.total ?? 0}</p>
              <p className="text-xs text-slate-400">Jami loglar</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-rose-100 rounded-xl flex items-center justify-center">
              <AlertCircle size={20} className="text-rose-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">{summary?.critical_emergency ?? 0}</p>
              <p className="text-xs text-slate-400">Critical / Emergency</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
              <AlertTriangle size={20} className="text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">{summary?.errors ?? 0}</p>
              <p className="text-xs text-slate-400">Xatoliklar</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-xl flex items-center justify-center">
              <Info size={20} className="text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">{summary?.warnings ?? 0}</p>
              <p className="text-xs text-slate-400">Ogohlantirishlar</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="relative flex-1 min-w-[160px]">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Qidirish..."
            />
          </div>
          <select
            value={hostname} onChange={(e) => setHostname(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Barcha hostlar</option>
            {hostnames.map((h) => <option key={h} value={h}>{h}</option>)}
          </select>
          <select
            value={severity} onChange={(e) => setSeverity(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>{s || "Barcha severity"}</option>
            ))}
          </select>
          <button onClick={handleFilter} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors">
            <Filter size={14} /> Filter
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="text-left px-4 py-3 font-medium text-slate-600">Vaqt</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Hostname</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">IP</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Facility</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Severity</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">App</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Message</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <>
                  <tr
                    key={entry.id}
                    onClick={() => setExpanded(expanded === entry.id ? null : entry.id)}
                    className="border-b border-slate-100 hover:bg-slate-50 cursor-pointer"
                  >
                    <td className="px-4 py-3 text-slate-600 whitespace-nowrap">
                      {new Date(entry.timestamp).toLocaleString("uz-UZ")}
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-800">{entry.hostname}</td>
                    <td className="px-4 py-3 text-slate-600">{entry.ip}</td>
                    <td className="px-4 py-3 text-slate-600">{entry.facility}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${severityColor[entry.severity] || "bg-slate-100 text-slate-600"}`}>
                        {entry.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{entry.app_name}</td>
                    <td className="px-4 py-3 text-slate-600 max-w-[300px] truncate">
                      {entry.message?.length > 100 ? `${entry.message.slice(0, 100)}...` : entry.message}
                    </td>
                  </tr>
                  {expanded === entry.id && (
                    <tr key={`${entry.id}-expanded`} className="bg-slate-50">
                      <td colSpan={7} className="px-4 py-3">
                        <div className="space-y-2 text-sm">
                          <p><span className="font-medium text-slate-700">To&apos;liq xabar:</span></p>
                          <p className="text-slate-600 whitespace-pre-wrap">{entry.message}</p>
                          {entry.raw_log && (
                            <>
                              <p className="font-medium text-slate-700 mt-2">Raw log:</p>
                              <pre className="text-xs text-slate-500 bg-slate-100 p-3 rounded-lg overflow-x-auto">{entry.raw_log}</pre>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
              {entries.length === 0 && (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-400">Log topilmadi</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {isAdmin && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Server size={18} className="text-slate-500" /> Hostlar bo&apos;yicha xulosa
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-4 py-3 font-medium text-slate-600">Hostname</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-600">Loglar soni</th>
                  <th className="text-left px-4 py-3 font-medium text-slate-600">Oxirgi ko&apos;rinish</th>
                </tr>
              </thead>
              <tbody>
                {hosts.map((h) => (
                  <tr key={h.hostname} className="border-b border-slate-100">
                    <td className="px-4 py-3 font-medium text-slate-800">{h.hostname}</td>
                    <td className="px-4 py-3 text-slate-600">{h.log_count}</td>
                    <td className="px-4 py-3 text-slate-600">{new Date(h.last_seen).toLocaleString("uz-UZ")}</td>
                  </tr>
                ))}
                {hosts.length === 0 && (
                  <tr>
                    <td colSpan={3} className="text-center py-8 text-slate-400">Host topilmadi</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
