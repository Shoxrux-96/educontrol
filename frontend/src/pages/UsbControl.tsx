import { useState, useEffect } from "react";
import { Usb, HardDrive, Search, Filter, XCircle, CheckCircle, Clock } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface UsbEvent {
  id: string;
  device_name: string;
  device_label?: string;
  action: "mounted" | "unmounted" | "blocked";
  vendor?: string;
  serial?: string;
  capacity?: string;
  filesystem?: string;
  computer_name?: string;
  computer_id?: string;
  username?: string;
  blocked: boolean;
  detected_at: string;
}

interface UsbStats {
  total_events: number;
  blocked_count: number;
  unique_devices: number;
  latest_event_time?: string;
}

interface DailyCount {
  date: string;
  count: number;
}

const actionColors: Record<string, string> = {
  mounted: "bg-emerald-100 text-emerald-700",
  unmounted: "bg-slate-100 text-slate-600",
  blocked: "bg-rose-100 text-rose-700",
};

export default function UsbControl() {
  const [events, setEvents] = useState<UsbEvent[]>([]);
  const [stats, setStats] = useState<UsbStats | null>(null);
  const [history, setHistory] = useState<DailyCount[]>([]);
  const [search, setSearch] = useState("");
  const [computerId, setComputerId] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [showBlockedOnly, setShowBlockedOnly] = useState(false);
  const [computers, setComputers] = useState<{ id: string; name: string }[]>([]);
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchStats();
    fetchHistory();
    api.get<{ items: { id: string; name: string }[] }>("/computers").then((r) => setComputers(r.data.items || [])).catch(() => {});
  }, []);

  useEffect(() => {
    const delay = setTimeout(() => fetchEvents(), 300);
    return () => clearTimeout(delay);
  }, [search, computerId, dateFrom, dateTo]);

  const fetchStats = async () => {
    try {
      const { data } = await api.get<UsbStats>("/security/usb/stats");
      setStats(data);
    } catch {
      /* ignore */
    }
  };

  const fetchHistory = async () => {
    try {
      const { data } = await api.get<DailyCount[]>("/security/usb/history/daily");
      setHistory(data || []);
    } catch {
      /* ignore */
    }
  };

  const fetchEvents = async () => {
    try {
      const params: Record<string, string | number> = { limit: 200 };
      if (search) params.search = search;
      if (computerId) params.computer_id = computerId;
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      const { data } = await api.get<{ items: UsbEvent[] }>("/security/usb", { params });
      setEvents(data.items || []);
    } catch {
      /* ignore */
    }
  };

  const toggleBlocked = async (eventId: string, blocked: boolean) => {
    try {
      await api.post(`/security/usb/${eventId}/block`, { blocked: !blocked });
      fetchEvents();
      fetchStats();
    } catch {
      /* ignore */
    }
  };

  const filteredEvents = showBlockedOnly ? events.filter((e) => e.action === "blocked") : events;
  const maxHistory = Math.max(...history.map((h) => h.count), 1);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">USB Qurilmalar</h1>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
              <Usb size={20} className="text-indigo-600" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Jami hodisalar</p>
              <p className="text-xl font-bold text-slate-800">{stats?.total_events ?? 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-rose-100 rounded-xl flex items-center justify-center">
              <XCircle size={20} className="text-rose-600" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Bloklangan</p>
              <p className="text-xl font-bold text-slate-800">{stats?.blocked_count ?? 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
              <HardDrive size={20} className="text-emerald-600" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Unikal qurilmalar</p>
              <p className="text-xl font-bold text-slate-800">{stats?.unique_devices ?? 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
              <Clock size={20} className="text-amber-600" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Oxirgi hodisa</p>
              <p className="text-sm font-bold text-slate-800">
                {stats?.latest_event_time ? new Date(stats.latest_event_time).toLocaleString("uz-UZ") : "—"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {history.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">So'nggi 30 kunlik USB faollik</h3>
          <div className="flex items-end gap-1 h-28">
            {history.map((d) => (
              <div key={d.date} className="flex-1 flex flex-col items-center group relative">
                <div
                  className="w-full bg-indigo-500 rounded-t hover:bg-indigo-600 transition-colors cursor-pointer"
                  style={{ height: `${(d.count / maxHistory) * 100}%`, minHeight: d.count > 0 ? 4 : 0 }}
                  title={`${d.date}: ${d.count} ta`}
                />
                {history.length <= 31 && (
                  <span className="text-[10px] text-slate-400 mt-1 truncate w-full text-center">
                    {d.date.slice(5)}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
        <div className="flex items-center gap-3 mb-4 flex-wrap">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Qurilma nomi, labeli yoki foydalanuvchi..."
            />
          </div>
          <select
            value={computerId} onChange={(e) => setComputerId(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Barcha kompyuterlar</option>
            {computers.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <input
            type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)}
            className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={() => setShowBlockedOnly(!showBlockedOnly)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              showBlockedOnly ? "bg-rose-100 text-rose-700" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            <Filter size={14} /> Bloklanganlar
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs text-slate-400 uppercase tracking-wider">
                <th className="py-3 pr-4">Qurilma</th>
                <th className="py-3 pr-4">Label</th>
                <th className="py-3 pr-4">Holat</th>
                <th className="py-3 pr-4">Vendor</th>
                <th className="py-3 pr-4">Serial</th>
                <th className="py-3 pr-4">Hajm</th>
                <th className="py-3 pr-4">Fayl tizimi</th>
                <th className="py-3 pr-4">Kompyuter</th>
                <th className="py-3 pr-4">Foydalanuvchi</th>
                <th className="py-3 pr-4">Blok</th>
                <th className="py-3 pr-4">Vaqt</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((e) => (
                <tr key={e.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="py-3 pr-4 font-medium text-slate-800">{e.device_name}</td>
                  <td className="py-3 pr-4 text-slate-600">{e.device_label || "—"}</td>
                  <td className="py-3 pr-4">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${actionColors[e.action]}`}>
                      {e.action}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-slate-600">{e.vendor || "—"}</td>
                  <td className="py-3 pr-4 text-slate-600 font-mono text-xs">{e.serial || "—"}</td>
                  <td className="py-3 pr-4 text-slate-600">{e.capacity || "—"}</td>
                  <td className="py-3 pr-4 text-slate-600">{e.filesystem || "—"}</td>
                  <td className="py-3 pr-4 text-slate-600">{e.computer_name || "—"}</td>
                  <td className="py-3 pr-4 text-slate-600">{e.username || "—"}</td>
                  <td className="py-3 pr-4">
                    {isAdmin ? (
                      <button
                        onClick={() => toggleBlocked(e.id, e.blocked)}
                        className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-lg transition-colors ${
                          e.blocked
                            ? "bg-rose-100 text-rose-700 hover:bg-rose-200"
                            : "bg-emerald-100 text-emerald-700 hover:bg-emerald-200"
                        }`}
                      >
                        {e.blocked ? <XCircle size={12} /> : <CheckCircle size={12} />}
                        {e.blocked ? "Blok" : "Ochiq"}
                      </button>
                    ) : (
                      <span className={`text-xs font-medium ${e.blocked ? "text-rose-600" : "text-emerald-600"}`}>
                        {e.blocked ? "Ha" : "Yo'q"}
                      </span>
                    )}
                  </td>
                  <td className="py-3 pr-4 text-slate-400 text-xs whitespace-nowrap">
                    {new Date(e.detected_at).toLocaleString("uz-UZ")}
                  </td>
                </tr>
              ))}
              {filteredEvents.length === 0 && (
                <tr>
                  <td colSpan={11} className="py-12 text-center text-slate-400">USB hodisalari topilmadi</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
