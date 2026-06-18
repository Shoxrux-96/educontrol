import { useState, useEffect } from "react";
import {
  Plus, Edit3, Trash2, X, Router, Monitor, Wifi, Printer, Camera,
  Server, Shield, Radio, HardDrive, Network, WifiOff
} from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface NetworkDevice {
  id: string;
  hostname: string;
  ip_address?: string;
  mac_address?: string;
  device_type: string;
  vendor?: string;
  model?: string;
  parent_id?: string | null;
  connection_type?: string;
  port_count?: number;
  notes?: string;
  is_monitored: boolean;
  created_at: string;
  children?: NetworkDevice[];
}

interface DeviceForm {
  hostname: string;
  ip_address: string;
  mac_address: string;
  device_type: string;
  vendor: string;
  model: string;
  parent_id: string;
  connection_type: string;
  port_count: string;
  notes: string;
}

const emptyForm: DeviceForm = {
  hostname: "", ip_address: "", mac_address: "", device_type: "router",
  vendor: "", model: "", parent_id: "", connection_type: "wired",
  port_count: "", notes: "",
};

const deviceTypes = [
  "router", "switch", "access_point", "printer", "camera",
  "computer", "server", "firewall_device", "modem", "other",
];

const deviceIcons: Record<string, any> = {
  router: Router, switch: Network, access_point: Wifi, printer: Printer,
  camera: Camera, computer: Monitor, server: Server,
  firewall_device: Shield, modem: Radio, other: HardDrive,
};

const deviceColors: Record<string, string> = {
  router: "text-orange-500", switch: "text-blue-500",
  access_point: "text-violet-500", printer: "text-rose-500",
  camera: "text-cyan-500", computer: "text-emerald-500",
  server: "text-indigo-500", firewall_device: "text-red-500",
  modem: "text-amber-500", other: "text-slate-500",
};

function buildTree(devices: NetworkDevice[]): NetworkDevice[] {
  const map = new Map<string, NetworkDevice>();
  const roots: NetworkDevice[] = [];
  devices.forEach((d) => map.set(d.id, { ...d, children: [] }));
  devices.forEach((d) => {
    const node = map.get(d.id)!;
    if (d.parent_id && map.has(d.parent_id)) {
      map.get(d.parent_id)!.children!.push(node);
    } else {
      roots.push(node);
    }
  });
  return roots;
}

function TreeNode({ device, depth = 0 }: { device: NetworkDevice; depth?: number }) {
  const Icon = deviceIcons[device.device_type] || HardDrive;
  return (
    <div className="select-none">
      <div
        className="flex items-center gap-3 px-3 py-2.5 hover:bg-slate-50 rounded-lg transition-colors"
        style={{ marginLeft: depth * 24 }}
      >
        <div className="w-8 h-8 bg-white rounded-xl border border-slate-200 flex items-center justify-center flex-shrink-0">
          <Icon size={16} className={deviceColors[device.device_type] || "text-slate-500"} />
        </div>
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <span className="font-medium text-slate-800 text-sm truncate">{device.hostname}</span>
          {device.ip_address && (
            <span className="text-xs text-slate-400 font-mono hidden sm:inline">{device.ip_address}</span>
          )}
        </div>
        <span className={`inline-block w-2 h-2 rounded-full flex-shrink-0 ${device.is_monitored ? "bg-emerald-500" : "bg-slate-300"}`}
          title={device.is_monitored ? "Monitored" : "Not monitored"} />
      </div>
      {device.children && device.children.length > 0 && (
        <div className="relative">
          {device.children.map((child) => (
            <TreeNode key={child.id} device={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function NetworkTopology() {
  const { user } = useAuth();
  const [devices, setDevices] = useState<NetworkDevice[]>([]);
  const [topology, setTopology] = useState<NetworkDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<NetworkDevice | null>(null);
  const [form, setForm] = useState<DeviceForm>(emptyForm);
  const [search, setSearch] = useState("");

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [devRes, topRes] = await Promise.all([
        api.get<NetworkDevice[]>("/network/devices").catch(() => ({ data: [] })),
        api.get<NetworkDevice[]>("/network/topology").catch(() => ({ data: [] })),
      ]);
      const flat = devRes.data || [];
      setDevices(flat);
      setTopology(topRes.data || []);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const tree = buildTree(topology.length > 0 ? topology : devices);

  const openAdd = () => {
    setEditing(null);
    setForm(emptyForm);
    setShowModal(true);
  };

  const openEdit = (d: NetworkDevice) => {
    setEditing(d);
    setForm({
      hostname: d.hostname,
      ip_address: d.ip_address || "",
      mac_address: d.mac_address || "",
      device_type: d.device_type,
      vendor: d.vendor || "",
      model: d.model || "",
      parent_id: d.parent_id || "",
      connection_type: d.connection_type || "wired",
      port_count: d.port_count?.toString() || "",
      notes: d.notes || "",
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    const payload: Record<string, any> = {
      hostname: form.hostname,
      ip_address: form.ip_address || undefined,
      mac_address: form.mac_address || undefined,
      device_type: form.device_type,
      vendor: form.vendor || undefined,
      model: form.model || undefined,
      parent_id: form.parent_id || null,
      connection_type: form.connection_type || undefined,
      port_count: form.port_count ? Number(form.port_count) : undefined,
      notes: form.notes || undefined,
    };
    try {
      if (editing) {
        await api.patch(`/network/devices/${editing.id}`, payload);
      } else {
        await api.post("/network/devices", payload);
      }
      setShowModal(false);
      fetchData();
    } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/network/devices/${id}`);
      fetchData();
    } catch { /* ignore */ }
  };

  const filtered = devices.filter((d) =>
    d.hostname.toLowerCase().includes(search.toLowerCase()) ||
    d.ip_address?.includes(search) ||
    d.mac_address?.includes(search)
  );

  const deviceTypeBadge = (t: string) => {
    const m: Record<string, string> = {
      router: "bg-orange-100 text-orange-700",
      switch: "bg-blue-100 text-blue-700",
      access_point: "bg-violet-100 text-violet-700",
      printer: "bg-rose-100 text-rose-700",
      camera: "bg-cyan-100 text-cyan-700",
      computer: "bg-emerald-100 text-emerald-700",
      server: "bg-indigo-100 text-indigo-700",
      firewall_device: "bg-red-100 text-red-700",
      modem: "bg-amber-100 text-amber-700",
      other: "bg-slate-100 text-slate-600",
    };
    return m[t] || "bg-slate-100 text-slate-600";
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Network Topology</h1>
        <div className="flex items-center gap-3">
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            className="pl-3 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Search..." />
          <button onClick={openAdd} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
            <Plus size={16} /> Add Device
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : (
        <>
          <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
            <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-3">Topology View</h2>
            {tree.length > 0 ? (
              tree.map((node) => <TreeNode key={node.id} device={node} />)
            ) : (
              <div className="text-center py-8 text-slate-400">No devices found</div>
            )}
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-200">
              <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider">All Devices</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                    <th className="text-left px-4 py-3 font-medium">Hostname</th>
                    <th className="text-left px-4 py-3 font-medium">IP Address</th>
                    <th className="text-left px-4 py-3 font-medium">MAC Address</th>
                    <th className="text-left px-4 py-3 font-medium">Type</th>
                    <th className="text-left px-4 py-3 font-medium">Vendor</th>
                    <th className="text-left px-4 py-3 font-medium">Model</th>
                    <th className="text-center px-4 py-3 font-medium">Status</th>
                    <th className="text-right px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filtered.map((d) => (
                    <tr key={d.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-800">{d.hostname}</td>
                      <td className="px-4 py-3 text-slate-600 font-mono text-xs">{d.ip_address || "—"}</td>
                      <td className="px-4 py-3 text-slate-600 font-mono text-xs">{d.mac_address || "—"}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${deviceTypeBadge(d.device_type)}`}>
                          {d.device_type.replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-600">{d.vendor || "—"}</td>
                      <td className="px-4 py-3 text-slate-600">{d.model || "—"}</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`inline-block w-2 h-2 rounded-full ${d.is_monitored ? "bg-emerald-500" : "bg-slate-300"}`}
                          title={d.is_monitored ? "Monitored" : "Not monitored"} />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button onClick={() => openEdit(d)} className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg">
                          <Edit3 size={14} />
                        </button>
                        <button onClick={() => handleDelete(d.id)} className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg ml-1">
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {filtered.length === 0 && <div className="text-center py-12 text-slate-400">No devices found</div>}
          </div>
        </>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">{editing ? "Edit Device" : "Add Device"}</h2>
              <button onClick={() => setShowModal(false)} className="p-1 text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Hostname</label>
                  <input type="text" value={form.hostname} onChange={(e) => setForm({ ...form, hostname: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Device Type</label>
                  <select value={form.device_type} onChange={(e) => setForm({ ...form, device_type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    {deviceTypes.map((t) => (
                      <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">IP Address</label>
                  <input type="text" value={form.ip_address} onChange={(e) => setForm({ ...form, ip_address: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">MAC Address</label>
                  <input type="text" value={form.mac_address} onChange={(e) => setForm({ ...form, mac_address: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Vendor</label>
                  <input type="text" value={form.vendor} onChange={(e) => setForm({ ...form, vendor: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Model</label>
                  <input type="text" value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Parent Device</label>
                  <select value={form.parent_id} onChange={(e) => setForm({ ...form, parent_id: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">None (Root)</option>
                    {devices.filter((d) => d.id !== editing?.id).map((d) => (
                      <option key={d.id} value={d.id}>{d.hostname} ({d.device_type})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Connection Type</label>
                  <select value={form.connection_type} onChange={(e) => setForm({ ...form, connection_type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="wired">Wired</option>
                    <option value="wireless">Wireless</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Port Count</label>
                  <input type="number" value={form.port_count} onChange={(e) => setForm({ ...form, port_count: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Notes</label>
                <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  rows={3} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
              </div>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
              <button onClick={handleSave} className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                {editing ? "Save" : "Add"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
