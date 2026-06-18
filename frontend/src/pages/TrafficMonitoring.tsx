import { useState, useEffect, useRef } from "react";
import { ArrowUp, ArrowDown, Activity, Users, RefreshCw } from "lucide-react";
import api from "../api/client";

interface TrafficSummary {
  total_uploaded: number;
  total_downloaded: number;
  total_connections: number;
  active_connections: number;
}

interface TopUser {
  username: string;
  computer_name: string;
  uploaded: number;
  downloaded: number;
  total: number;
}

interface TrafficLog {
  id: string;
  computer_name: string;
  username?: string;
  source_ip: string;
  dest_ip: string;
  destination: string;
  bytes_sent: number;
  bytes_received: number;
  protocol: string;
  timestamp: string;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

export default function TrafficMonitoring() {
  const [summary, setSummary] = useState<TrafficSummary | null>(null);
  const [topUsers, setTopUsers] = useState<TopUser[]>([]);
  const [logs, setLogs] = useState<TrafficLog[]>([]);
  const [loading, setLoading] = useState(true);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    fetchAll();
    intervalRef.current = setInterval(fetchAll, 10000);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, []);

  const fetchAll = async () => {
    try {
      const [s, u, l] = await Promise.all([
        api.get<TrafficSummary>("/internet/traffic/summary"),
        api.get<TopUser[]>("/internet/traffic/top-users"),
        api.get<TrafficLog[]>("/internet/traffic/realtime", { params: { minutes: 5 } }),
      ]);
      setSummary(s.data);
      setTopUsers(u.data);
      setLogs(l.data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  if (loading) {
    return <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">Trafik monitoringi</h1>
        <button onClick={fetchAll} className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">
          <RefreshCw size={14} /> Yangilash
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500 font-medium">Yuklangan</span>
            <ArrowUp size={16} className="text-emerald-500" />
          </div>
          <p className="text-2xl font-bold text-slate-800">{formatBytes(summary?.total_uploaded || 0)}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500 font-medium">Yuklab olingan</span>
            <ArrowDown size={16} className="text-blue-500" />
          </div>
          <p className="text-2xl font-bold text-slate-800">{formatBytes(summary?.total_downloaded || 0)}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500 font-medium">Faol ulanishlar</span>
            <Activity size={16} className="text-indigo-500" />
          </div>
          <p className="text-2xl font-bold text-slate-800">{summary?.active_connections ?? 0}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500 font-medium">Jami ulanishlar</span>
            <Users size={16} className="text-amber-500" />
          </div>
          <p className="text-2xl font-bold text-slate-800">{summary?.total_connections ?? 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200">
          <div className="px-5 py-4 border-b border-slate-200">
            <h2 className="font-semibold text-slate-800">Top foydalanuvchilar</h2>
          </div>
          <div className="p-5">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-slate-500 text-xs uppercase tracking-wider">
                  <th className="text-left pb-2 font-medium">Foydalanuvchi</th>
                  <th className="text-left pb-2 font-medium">Kompyuter</th>
                  <th className="text-right pb-2 font-medium">Yuklangan</th>
                  <th className="text-right pb-2 font-medium">Yuklab olingan</th>
                  <th className="text-right pb-2 font-medium">Jami</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {topUsers.map((u, i) => (
                  <tr key={i} className="text-slate-700">
                    <td className="py-2.5 font-medium">{u.username}</td>
                    <td className="py-2.5 text-slate-500">{u.computer_name}</td>
                    <td className="py-2.5 text-right text-emerald-600">{formatBytes(u.uploaded)}</td>
                    <td className="py-2.5 text-right text-blue-600">{formatBytes(u.downloaded)}</td>
                    <td className="py-2.5 text-right font-semibold">{formatBytes(u.total)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {topUsers.length === 0 && <p className="text-center py-6 text-slate-400">Ma'lumot mavjud emas</p>}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200">
          <div className="px-5 py-4 border-b border-slate-200">
            <h2 className="font-semibold text-slate-800">So'nggi trafik (5 daqiqa)</h2>
          </div>
          <div className="p-5 max-h-96 overflow-y-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-slate-500 text-xs uppercase tracking-wider">
                  <th className="text-left pb-2 font-medium">Manba</th>
                  <th className="text-left pb-2 font-medium">Maqsad</th>
                  <th className="text-right pb-2 font-medium">Yuborilgan</th>
                  <th className="text-right pb-2 font-medium">Qabul</th>
                  <th className="text-right pb-2 font-medium">Vaqt</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.map((l) => (
                  <tr key={l.id} className="text-slate-700 text-xs">
                    <td className="py-2">
                      <div className="font-medium">{l.computer_name}</div>
                      <div className="text-slate-400">{l.source_ip}</div>
                    </td>
                    <td className="py-2">
                      <div className="font-medium">{l.destination}</div>
                      <div className="text-slate-400">{l.protocol}</div>
                    </td>
                    <td className="py-2 text-right text-emerald-600">{formatBytes(l.bytes_sent)}</td>
                    <td className="py-2 text-right text-blue-600">{formatBytes(l.bytes_received)}</td>
                    <td className="py-2 text-right text-slate-400 whitespace-nowrap">
                      {new Date(l.timestamp).toLocaleTimeString("uz-UZ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {logs.length === 0 && <p className="text-center py-6 text-slate-400">Ma'lumot mavjud emas</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
