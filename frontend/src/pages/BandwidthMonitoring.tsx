import { useState, useEffect, useRef } from "react";
import { Activity, ArrowDown, ArrowUp, RefreshCw, TrendingUp } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface NetworkDevice {
  id: string;
  name: string;
  ip_address?: string;
  interface_name?: string;
}

interface BandwidthSummary {
  avg_in_bps: number;
  avg_out_bps: number;
  peak_in_bps: number;
  peak_out_bps: number;
  avg_utilization: number;
}

interface BandwidthRecord {
  id: string;
  device_id: string;
  device_name?: string;
  interface_name?: string;
  bytes_in: number;
  bytes_out: number;
  bits_in_per_sec: number;
  bits_out_per_sec: number;
  utilization: number;
  recorded_at: string;
}

function formatBits(bps: number): string {
  if (bps === 0) return "0 bps";
  const units = ["bps", "Kbps", "Mbps", "Gbps"];
  const i = Math.floor(Math.log(Math.abs(bps)) / Math.log(1000));
  return `${(bps / Math.pow(1000, i)).toFixed(1)} ${units[i]}`;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(Math.abs(bytes)) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

function BarChart({
  data,
  color,
  valueKey,
  label,
  format,
}: {
  data: BandwidthRecord[];
  color: string;
  valueKey: "bits_in_per_sec" | "bits_out_per_sec" | "utilization";
  label: string;
  format: (v: number) => string;
}) {
  const values = data.map((r) => r[valueKey]);
  const max = Math.max(...values, 1);

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="font-semibold text-slate-800 mb-3">{label}</h3>
      <div className="flex items-end gap-[2px] h-40">
        {data.length === 0 ? (
          <div className="w-full text-center text-slate-400 text-sm self-center">
            Ma'lumot mavjud emas
          </div>
        ) : (
          data.map((r, i) => (
            <div
              key={r.id || i}
              className="flex-1 rounded-t transition-all duration-300 min-w-[2px]"
              style={{
                height: `${Math.max((r[valueKey] / max) * 100, 1)}%`,
                backgroundColor: color,
              }}
              title={`${format(r[valueKey])} - ${new Date(r.recorded_at).toLocaleString()}`}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default function BandwidthMonitoring() {
  const { user } = useAuth();
  const [devices, setDevices] = useState<NetworkDevice[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  const [summary, setSummary] = useState<BandwidthSummary | null>(null);
  const [records, setRecords] = useState<BandwidthRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [recording, setRecording] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    api
      .get<{ items: NetworkDevice[] }>("/network/devices")
      .then((r) => {
        const items = r.data.items || r.data || [];
        setDevices(items);
        if (items.length > 0 && !selectedDeviceId) {
          setSelectedDeviceId(items[0].id);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedDeviceId) {
      setLoading(false);
      return;
    }
    fetchData();
    intervalRef.current = setInterval(fetchData, 15000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [selectedDeviceId]);

  const fetchData = async () => {
    try {
      const [s, r] = await Promise.all([
        api.get<BandwidthSummary>("/network/bandwidth/summary", {
          params: { device_id: selectedDeviceId },
        }),
        api.get<{ items: BandwidthRecord[] }>("/network/bandwidth", {
          params: { device_id: selectedDeviceId, limit: 60 },
        }),
      ]);
      setSummary(s.data);
      setRecords(r.data.items || r.data || []);
    } catch {
      /* ignore */
    }
    setLoading(false);
  };

  const handleRecord = async () => {
    if (!selectedDeviceId) return;
    setRecording(true);
    try {
      await api.post("/network/bandwidth", { device_id: selectedDeviceId });
      await fetchData();
    } catch {
      /* ignore */
    }
    setRecording(false);
  };

  const sorted = [...records].sort(
    (a, b) =>
      new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()
  );

  const isAdmin = user?.role === "admin" || user?.role === "owner";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-xl font-bold text-slate-800">
          Bandwidth Monitoring
        </h1>
        <div className="flex items-center gap-3">
          <select
            value={selectedDeviceId}
            onChange={(e) => setSelectedDeviceId(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
          >
            <option value="">Device tanlang</option>
            {devices.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
                {d.ip_address ? ` (${d.ip_address})` : ""}
              </option>
            ))}
          </select>
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg"
          >
            <RefreshCw size={14} /> Yangilash
          </button>
          {isAdmin && (
            <button
              onClick={handleRecord}
              disabled={recording}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              <Activity size={14} />
              {recording ? "Yozilmoqda..." : "Record"}
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>
      ) : !selectedDeviceId ? (
        <div className="text-center py-12 text-slate-400">
          Iltimos, device tanlang
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-500 font-medium">
                  Avg In
                </span>
                <ArrowDown size={16} className="text-blue-500" />
              </div>
              <p className="text-xl font-bold text-slate-800">
                {formatBits(summary?.avg_in_bps ?? 0)}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-500 font-medium">
                  Avg Out
                </span>
                <ArrowUp size={16} className="text-emerald-500" />
              </div>
              <p className="text-xl font-bold text-slate-800">
                {formatBits(summary?.avg_out_bps ?? 0)}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-500 font-medium">
                  Peak In
                </span>
                <TrendingUp size={16} className="text-orange-500" />
              </div>
              <p className="text-xl font-bold text-slate-800">
                {formatBits(summary?.peak_in_bps ?? 0)}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-500 font-medium">
                  Peak Out
                </span>
                <TrendingUp size={16} className="text-red-500" />
              </div>
              <p className="text-xl font-bold text-slate-800">
                {formatBits(summary?.peak_out_bps ?? 0)}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-500 font-medium">
                  Avg Utilization
                </span>
                <Activity size={16} className="text-purple-500" />
              </div>
              <p className="text-xl font-bold text-slate-800">
                {summary?.avg_utilization?.toFixed(1) ?? "0.0"}%
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <BarChart
              data={sorted}
              color="#3b82f6"
              valueKey="bits_in_per_sec"
              label="Download Speed"
              format={formatBits}
            />
            <BarChart
              data={sorted}
              color="#10b981"
              valueKey="bits_out_per_sec"
              label="Upload Speed"
              format={formatBits}
            />
            <BarChart
              data={sorted}
              color="#8b5cf6"
              valueKey="utilization"
              label="Utilization %"
              format={(v) => `${v.toFixed(1)}%`}
            />
          </div>

          <div className="bg-white rounded-xl border border-slate-200">
            <div className="px-5 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">
                Bandwidth Records
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-slate-500 text-xs uppercase tracking-wider">
                    <th className="text-left px-5 py-3 font-medium">Device</th>
                    <th className="text-left px-5 py-3 font-medium">
                      Interface
                    </th>
                    <th className="text-right px-5 py-3 font-medium">
                      In (bytes)
                    </th>
                    <th className="text-right px-5 py-3 font-medium">
                      Out (bytes)
                    </th>
                    <th className="text-right px-5 py-3 font-medium">
                      In Speed
                    </th>
                    <th className="text-right px-5 py-3 font-medium">
                      Out Speed
                    </th>
                    <th className="text-right px-5 py-3 font-medium">
                      Utilization
                    </th>
                    <th className="text-right px-5 py-3 font-medium">
                      Recorded At
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[...sorted].reverse().map((r) => (
                    <tr key={r.id} className="text-slate-700">
                      <td className="px-5 py-3 font-medium">
                        {r.device_name || r.device_id}
                      </td>
                      <td className="px-5 py-3 text-slate-500">
                        {r.interface_name || "-"}
                      </td>
                      <td className="px-5 py-3 text-right">
                        {formatBytes(r.bytes_in)}
                      </td>
                      <td className="px-5 py-3 text-right">
                        {formatBytes(r.bytes_out)}
                      </td>
                      <td className="px-5 py-3 text-right text-blue-600">
                        {formatBits(r.bits_in_per_sec)}
                      </td>
                      <td className="px-5 py-3 text-right text-emerald-600">
                        {formatBits(r.bits_out_per_sec)}
                      </td>
                      <td className="px-5 py-3 text-right">
                        {r.utilization.toFixed(1)}%
                      </td>
                      <td className="px-5 py-3 text-right text-slate-400 whitespace-nowrap">
                        {new Date(r.recorded_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {sorted.length === 0 && (
                <p className="text-center py-6 text-slate-400">
                  Ma'lumot mavjud emas
                </p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
