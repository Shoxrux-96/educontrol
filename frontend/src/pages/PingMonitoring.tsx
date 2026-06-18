import { useState, useEffect } from "react";
import { Wifi, WifiOff, AlertTriangle, RefreshCw, Loader2, Activity } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface PingStatus {
  device_id: number;
  hostname: string;
  ip_address: string;
  status: string;
  latency_ms: number | null;
  packet_loss: number | null;
  last_check: string;
}

interface PingResult {
  id: number;
  device_id: number | null;
  hostname: string;
  ip_address: string;
  status: string;
  latency_ms: number | null;
  packet_loss: number | null;
  jitter_ms: number | null;
  checked_at: string;
}

interface Device {
  id: number;
  hostname: string;
  ip_address: string;
}

export default function PingMonitoring() {
  const { user } = useAuth();
  const [statuses, setStatuses] = useState<PingStatus[]>([]);
  const [results, setResults] = useState<PingResult[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [deviceFilter, setDeviceFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [pinging, setPinging] = useState<number | null>(null);

  useEffect(() => {
    fetchAll();
    const iv = setInterval(fetchAll, 30000);
    return () => clearInterval(iv);
  }, []);

  const fetchAll = async () => {
    try {
      const [statusRes, devicesRes] = await Promise.all([
        api.get<PingStatus[]>("/network/ping-status"),
        api.get<Device[]>("/network/devices"),
      ]);
      setStatuses(statusRes.data);
      setDevices(devicesRes.data);
    } catch { /* ignore */ }
    fetchResults();
    setLoading(false);
  };

  const fetchResults = async (deviceId?: string) => {
    try {
      const params: Record<string, string | number> = { limit: 50 };
      const id = deviceId ?? deviceFilter;
      if (id) params.device_id = id;
      const r = await api.get<PingResult[]>("/network/ping-results", { params });
      setResults(r.data);
    } catch { /* ignore */ }
  };

  const manualPing = async (deviceId: number) => {
    setPinging(deviceId);
    try {
      await api.post("/network/ping-results", { device_id: deviceId });
      await fetchAll();
    } catch { /* ignore */ }
    setPinging(null);
  };

  const handleFilterChange = (val: string) => {
    setDeviceFilter(val);
    fetchResults(val);
  };

  const cardStatus = (s: PingStatus) => {
    if (s.status === "dead") return "rose";
    if ((s.latency_ms ?? 0) > 100 || (s.packet_loss ?? 0) > 5) return "amber";
    return "emerald";
  };

  if (loading) {
    return <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">Ping Monitoring</h1>
        <button
          onClick={fetchAll}
          className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
        >
          <RefreshCw size={14} /> Yangilash
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {statuses.map((s) => {
          const color = cardStatus(s);
          const badge =
            color === "emerald" ? "bg-emerald-100 text-emerald-700" :
            color === "amber" ? "bg-amber-100 text-amber-700" :
            "bg-rose-100 text-rose-700";
          const border =
            color === "emerald" ? "border-emerald-200" :
            color === "amber" ? "border-amber-200" :
            "border-rose-200";
          const icon =
            color === "emerald" ? <Wifi size={20} className="text-emerald-500" /> :
            color === "amber" ? <AlertTriangle size={20} className="text-amber-500" /> :
            <WifiOff size={20} className="text-rose-400" />;

          return (
            <div key={s.device_id} className={`bg-white rounded-xl border-2 p-5 transition-shadow hover:shadow-md ${border}`}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    color === "emerald" ? "bg-emerald-50" :
                    color === "amber" ? "bg-amber-50" :
                    "bg-rose-50"
                  }`}>
                    {icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">{s.hostname}</h3>
                    <p className="text-xs text-slate-400">{s.ip_address}</p>
                  </div>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 text-xs mb-3">
                <span className={`px-2 py-1 rounded-full font-medium ${badge}`}>
                  {color === "emerald" ? "Alive" : color === "amber" ? "Warning" : "Dead"}
                </span>
              </div>
              <div className="space-y-1 text-xs text-slate-600">
                <p>Latency: {s.latency_ms != null ? `${s.latency_ms} ms` : "\u2014"}</p>
                <p>Paket yo'qotish: {s.packet_loss != null ? `${s.packet_loss}%` : "\u2014"}</p>
                <p>Oxirgi tekshirish: {s.last_check ? new Date(s.last_check).toLocaleString("uz-UZ") : "\u2014"}</p>
              </div>
              <button
                onClick={() => manualPing(s.device_id)}
                disabled={pinging === s.device_id}
                className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 disabled:opacity-50 rounded-lg transition-colors"
              >
                {pinging === s.device_id ? <Loader2 size={14} className="animate-spin" /> : <Activity size={14} />}
                Manual Ping
              </button>
            </div>
          );
        })}
        {statuses.length === 0 && (
          <div className="col-span-full text-center py-12 text-slate-400">Monitoring qilinadigan qurilmalar mavjud emas</div>
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="font-semibold text-slate-800">Ping tarixi</h2>
          <select
            value={deviceFilter}
            onChange={(e) => handleFilterChange(e.target.value)}
            className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Barcha qurilmalar</option>
            {devices.map((d) => (
              <option key={d.id} value={d.id}>{d.hostname}</option>
            ))}
          </select>
        </div>
        <div className="p-5 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 text-xs uppercase tracking-wider">
                <th className="text-left pb-2 font-medium">Qurilma</th>
                <th className="text-left pb-2 font-medium">IP</th>
                <th className="text-left pb-2 font-medium">Holat</th>
                <th className="text-right pb-2 font-medium">Latency</th>
                <th className="text-right pb-2 font-medium">Paket yo'qotish</th>
                <th className="text-right pb-2 font-medium">Jitter</th>
                <th className="text-right pb-2 font-medium">Tekshirilgan</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {results.map((r) => (
                <tr key={r.id} className="text-slate-700">
                  <td className="py-2.5 font-medium">{r.hostname}</td>
                  <td className="py-2.5 text-slate-500">{r.ip_address}</td>
                  <td className="py-2.5">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      r.status === "alive" ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"
                    }`}>
                      {r.status === "alive" ? "Alive" : "Dead"}
                    </span>
                  </td>
                  <td className="py-2.5 text-right">{r.latency_ms != null ? `${r.latency_ms} ms` : "\u2014"}</td>
                  <td className="py-2.5 text-right">{r.packet_loss != null ? `${r.packet_loss}%` : "\u2014"}</td>
                  <td className="py-2.5 text-right">{r.jitter_ms != null ? `${r.jitter_ms} ms` : "\u2014"}</td>
                  <td className="py-2.5 text-right text-slate-400 whitespace-nowrap">
                    {new Date(r.checked_at).toLocaleString("uz-UZ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {results.length === 0 && <p className="text-center py-6 text-slate-400">Ping natijalari mavjud emas</p>}
        </div>
      </div>
    </div>
  );
}
