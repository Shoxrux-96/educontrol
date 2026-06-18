import { useState, useEffect } from "react";
import { Wifi, Network, Printer, Server, Battery, Shield, Activity, Plus, Pencil, Trash2, RefreshCw, X } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

const DEVICE_TYPES = ["router", "switch", "printer", "server", "ups", "firewall"] as const;
type DeviceType = (typeof DEVICE_TYPES)[number];

const TYPE_ICONS: Record<DeviceType, typeof Wifi> = {
  router: Wifi,
  switch: Network,
  printer: Printer,
  server: Server,
  ups: Battery,
  firewall: Shield,
};

interface SnmpDevice {
  id: number;
  hostname: string;
  ip_address: string;
  device_type: DeviceType;
  vendor: string;
  model: string;
  version: string;
  snmp_version: string;
  community: string;
  snmp_user: string;
  auth_protocol: string;
  priv_protocol: string;
  poll_interval: number;
  uptime: string;
  reachable: boolean;
  last_poll: string;
}

interface Metric {
  id: number;
  name: string;
  value: number;
  unit: string;
  recorded_at: string;
}

interface DeviceForm {
  hostname: string;
  ip_address: string;
  device_type: DeviceType;
  snmp_version: string;
  community: string;
  snmp_user: string;
  auth_protocol: string;
  priv_protocol: string;
  vendor: string;
  model: string;
  poll_interval: number;
}

const emptyForm = (): DeviceForm => ({
  hostname: "",
  ip_address: "",
  device_type: "router",
  snmp_version: "v2c",
  community: "public",
  snmp_user: "",
  auth_protocol: "",
  priv_protocol: "",
  vendor: "",
  model: "",
  poll_interval: 300,
});

export default function SnmpMonitoring() {
  const { isAdmin } = useAuth();
  const [devices, setDevices] = useState<SnmpDevice[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<SnmpDevice | null>(null);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [typeFilter, setTypeFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<DeviceForm>(emptyForm());
  const [editingId, setEditingId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchDevices();
  }, [typeFilter]);

  const fetchDevices = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (typeFilter) params.device_type = typeFilter;
      const r = await api.get<{ items: SnmpDevice[] }>("/enterprise/snmp/devices", { params });
      setDevices(r.data.items || []);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const fetchMetrics = async (deviceId: number) => {
    try {
      const r = await api.get<{ items: Metric[] }>(`/enterprise/snmp/devices/${deviceId}/metrics/latest`);
      setMetrics(r.data.items || []);
    } catch { /* ignore */ }
  };

  const openAdd = () => {
    setForm(emptyForm());
    setEditingId(null);
    setShowForm(true);
  };

  const openEdit = (d: SnmpDevice) => {
    setForm({
      hostname: d.hostname,
      ip_address: d.ip_address,
      device_type: d.device_type,
      snmp_version: d.snmp_version,
      community: d.community || "",
      snmp_user: d.snmp_user || "",
      auth_protocol: d.auth_protocol || "",
      priv_protocol: d.priv_protocol || "",
      vendor: d.vendor || "",
      model: d.model || "",
      poll_interval: d.poll_interval || 300,
    });
    setEditingId(d.id);
    setShowForm(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editingId) {
        await api.patch(`/enterprise/snmp/devices/${editingId}`, form);
      } else {
        await api.post("/enterprise/snmp/devices", form);
      }
      setShowForm(false);
      await fetchDevices();
    } catch { /* ignore */ }
    setSaving(false);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Ushbu qurilmani o'chirishni tasdiqlaysizmi?")) return;
    try {
      await api.delete(`/enterprise/snmp/devices/${id}`);
      if (selectedDevice?.id === id) {
        setSelectedDevice(null);
        setMetrics([]);
      }
      await fetchDevices();
    } catch { /* ignore */ }
  };

  const handleSelectDevice = (d: SnmpDevice) => {
    setSelectedDevice(d);
    fetchMetrics(d.id);
  };

  const summary = {
    total: devices.length,
    reachable: devices.filter((d) => d.reachable).length,
    unreachable: devices.filter((d) => !d.reachable).length,
    byType: Object.fromEntries(
      DEVICE_TYPES.map((t) => [t, devices.filter((d) => d.device_type === t).length])
    ) as Record<DeviceType, number>,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">SNMP Monitoring</h1>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchDevices}
            className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <RefreshCw size={14} /> Yangilash
          </button>
          {isAdmin && (
            <button
              onClick={openAdd}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Plus size={14} /> Qurilma qo'shish
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
          <p className="text-2xl font-bold text-slate-800">{summary.total}</p>
          <p className="text-xs text-slate-500">Jami</p>
        </div>
        <div className="bg-white rounded-xl border border-emerald-200 p-4 text-center">
          <p className="text-2xl font-bold text-emerald-600">{summary.reachable}</p>
          <p className="text-xs text-slate-500">Reachable</p>
        </div>
        <div className="bg-white rounded-xl border border-rose-200 p-4 text-center">
          <p className="text-2xl font-bold text-rose-500">{summary.unreachable}</p>
          <p className="text-xs text-slate-500">Not reachable</p>
        </div>
        {DEVICE_TYPES.map((t) => {
          const Icon = TYPE_ICONS[t];
          return (
            <div key={t} className="bg-white rounded-xl border border-slate-200 p-4 text-center">
              <Icon size={18} className="mx-auto mb-1 text-slate-500" />
              <p className="text-lg font-bold text-slate-800">{summary.byType[t]}</p>
              <p className="text-xs text-slate-500 capitalize">{t}</p>
            </div>
          );
        })}
      </div>

      <div className="flex items-center gap-3">
        <span className="text-sm font-medium text-slate-600">Filtrlash:</span>
        {["", ...DEVICE_TYPES].map((t) => (
          <button
            key={t || "all"}
            onClick={() => setTypeFilter(t)}
            className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
              typeFilter === t
                ? "bg-indigo-50 border-indigo-300 text-indigo-700"
                : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
            }`}
          >
            {t ? (() => { const Icon = TYPE_ICONS[t as DeviceType]; return <Icon size={14} className="inline mr-1" />; })() : null}
            {t || "Barchasi"}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={`${selectedDevice ? "lg:col-span-2" : "lg:col-span-3"}`}>
          <div className="bg-white rounded-xl border border-slate-200">
            <div className="px-5 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">SNMP Devices</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-slate-500 text-xs uppercase tracking-wider">
                    <th className="text-left px-5 py-3 font-medium">Hostname</th>
                    <th className="text-left px-5 py-3 font-medium">IP</th>
                    <th className="text-left px-5 py-3 font-medium">Type</th>
                    <th className="text-left px-5 py-3 font-medium">Vendor</th>
                    <th className="text-left px-5 py-3 font-medium">Model</th>
                    <th className="text-left px-5 py-3 font-medium">Version</th>
                    <th className="text-left px-5 py-3 font-medium">SNMP</th>
                    <th className="text-left px-5 py-3 font-medium">Uptime</th>
                    <th className="text-left px-5 py-3 font-medium">Status</th>
                    <th className="text-right px-5 py-3 font-medium">Last Poll</th>
                    {isAdmin && <th className="text-right px-5 py-3 font-medium" />}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {devices.map((d) => {
                    const Icon = TYPE_ICONS[d.device_type] || Activity;
                    return (
                      <tr
                        key={d.id}
                        onClick={() => handleSelectDevice(d)}
                        className={`text-slate-700 cursor-pointer hover:bg-slate-50 transition-colors ${
                          selectedDevice?.id === d.id ? "bg-indigo-50" : ""
                        }`}
                      >
                        <td className="px-5 py-3 font-medium">{d.hostname}</td>
                        <td className="px-5 py-3 text-slate-500 font-mono">{d.ip_address}</td>
                        <td className="px-5 py-3">
                          <Icon size={16} className="text-slate-500" title={d.device_type} />
                        </td>
                        <td className="px-5 py-3 text-slate-500">{d.vendor || "-"}</td>
                        <td className="px-5 py-3 text-slate-500">{d.model || "-"}</td>
                        <td className="px-5 py-3 text-slate-500">{d.version || "-"}</td>
                        <td className="px-5 py-3">
                          <span className="px-2 py-0.5 bg-slate-100 rounded text-xs font-mono">{d.snmp_version}</span>
                        </td>
                        <td className="px-5 py-3 text-slate-500">{d.uptime || "-"}</td>
                        <td className="px-5 py-3">
                          <span
                            className={`inline-block w-2.5 h-2.5 rounded-full ${
                              d.reachable ? "bg-emerald-500" : "bg-red-500"
                            }`}
                            title={d.reachable ? "Reachable" : "Not reachable"}
                          />
                        </td>
                        <td className="px-5 py-3 text-right text-slate-400 whitespace-nowrap">
                          {d.last_poll ? new Date(d.last_poll).toLocaleString("uz-UZ") : "-"}
                        </td>
                        {isAdmin && (
                          <td className="px-5 py-3 text-right whitespace-nowrap">
                            <button
                              onClick={(e) => { e.stopPropagation(); openEdit(d); }}
                              className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                              title="Tahrirlash"
                            >
                              <Pencil size={14} />
                            </button>
                            <button
                              onClick={(e) => { e.stopPropagation(); handleDelete(d.id); }}
                              className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors ml-1"
                              title="O'chirish"
                            >
                              <Trash2 size={14} />
                            </button>
                          </td>
                        )}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {loading && <p className="text-center py-6 text-slate-400">Yuklanmoqda...</p>}
              {!loading && devices.length === 0 && (
                <p className="text-center py-6 text-slate-400">Qurilmalar topilmadi</p>
              )}
            </div>
          </div>
        </div>

        {selectedDevice && (
          <div className="bg-white rounded-xl border border-slate-200">
            <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
              <h2 className="font-semibold text-slate-800">
                {selectedDevice.hostname} - Metrics
              </h2>
              <button
                onClick={() => fetchMetrics(selectedDevice.id)}
                className="p-1.5 text-slate-400 hover:text-indigo-600 rounded-lg transition-colors"
                title="Yangilash"
              >
                <RefreshCw size={14} />
              </button>
            </div>
            <div className="p-5 space-y-3">
              {metrics.length === 0 && (
                <p className="text-center py-6 text-slate-400">Metrikalar mavjud emas</p>
              )}
              {metrics.map((m) => (
                <div
                  key={m.id}
                  className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                >
                  <div>
                    <p className="text-sm font-medium text-slate-700">{m.name}</p>
                    <p className="text-xs text-slate-400">
                      {new Date(m.recorded_at).toLocaleString("uz-UZ")}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-slate-800">
                      {m.value}
                    </p>
                    <p className="text-xs text-slate-500">{m.unit || ""}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h3 className="font-semibold text-slate-800">
                {editingId ? "Qurilmani tahrirlash" : "Yangi qurilma qo'shish"}
              </h3>
              <button onClick={() => setShowForm(false)} className="p-1 text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Hostname</label>
                  <input
                    type="text" value={form.hostname}
                    onChange={(e) => setForm({ ...form, hostname: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">IP Address</label>
                  <input
                    type="text" value={form.ip_address}
                    onChange={(e) => setForm({ ...form, ip_address: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Device Type</label>
                  <select
                    value={form.device_type}
                    onChange={(e) => setForm({ ...form, device_type: e.target.value as DeviceType })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  >
                    {DEVICE_TYPES.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">SNMP Version</label>
                  <select
                    value={form.snmp_version}
                    onChange={(e) => setForm({ ...form, snmp_version: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  >
                    <option value="v1">v1</option>
                    <option value="v2c">v2c</option>
                    <option value="v3">v3</option>
                  </select>
                </div>
              </div>
              {form.snmp_version === "v3" ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">SNMP User</label>
                    <input
                      type="text" value={form.snmp_user}
                      onChange={(e) => setForm({ ...form, snmp_user: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-600 mb-1">Auth Protocol</label>
                      <input
                        type="text" value={form.auth_protocol}
                        onChange={(e) => setForm({ ...form, auth_protocol: e.target.value })}
                        className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="MD5 / SHA"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-600 mb-1">Priv Protocol</label>
                      <input
                        type="text" value={form.priv_protocol}
                        onChange={(e) => setForm({ ...form, priv_protocol: e.target.value })}
                        className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="DES / AES"
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Community</label>
                  <input
                    type="text" value={form.community}
                    onChange={(e) => setForm({ ...form, community: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Vendor</label>
                  <input
                    type="text" value={form.vendor}
                    onChange={(e) => setForm({ ...form, vendor: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Model</label>
                  <input
                    type="text" value={form.model}
                    onChange={(e) => setForm({ ...form, model: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Poll Interval (seconds)</label>
                <input
                  type="number" value={form.poll_interval}
                  onChange={(e) => setForm({ ...form, poll_interval: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-200">
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Bekor qilish
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {saving ? "Saqlanmoqda..." : editingId ? "Yangilash" : "Qo'shish"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
