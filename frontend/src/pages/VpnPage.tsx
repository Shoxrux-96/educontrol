import { useState, useEffect } from "react";
import { Plus, Wifi, Users, X, Globe, Key } from "lucide-react";
import api from "../api/client";

interface VpnProfile {
  id: string;
  name: string;
  type: "wireguard" | "openvpn";
  server_address: string;
  port: number;
  status: "active" | "inactive" | "error";
  clients_count: number;
  created_at: string;
}

interface VpnClient {
  id: string;
  profile_id: string;
  profile_name: string;
  client_name: string;
  client_ip: string;
  connected_since: string;
  bytes_sent: number;
  bytes_received: number;
}

interface ProfileForm {
  name: string;
  type: string;
  server_address: string;
  port: string;
}

const emptyForm: ProfileForm = {
  name: "", type: "wireguard", server_address: "", port: "51820",
};

const statusBadge: Record<string, string> = {
  active: "bg-emerald-100 text-emerald-700",
  inactive: "bg-slate-100 text-slate-500",
  error: "bg-rose-100 text-rose-700",
};

export default function VpnPage() {
  const [profiles, setProfiles] = useState<VpnProfile[]>([]);
  const [clients, setClients] = useState<VpnClient[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<ProfileForm>(emptyForm);

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [p, c] = await Promise.all([
        api.get<VpnProfile[]>("/vpn/profiles"),
        api.get<VpnClient[]>("/vpn/clients"),
      ]);
      setProfiles(p.data);
      setClients(c.data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const handleCreate = async () => {
    try {
      await api.post("/vpn/profiles", {
        ...form,
        port: Number(form.port),
      });
      setShowModal(false);
      setForm(emptyForm);
      fetchAll();
    } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/vpn/profiles/${id}`);
      fetchAll();
    } catch { /* ignore */ }
  };

  const toggleStatus = async (profile: VpnProfile) => {
    const newStatus = profile.status === "active" ? "inactive" : "active";
    try {
      await api.patch(`/vpn/profiles/${profile.id}`, { status: newStatus });
      setProfiles((prev) => prev.map((p) => p.id === profile.id ? { ...p, status: newStatus } : p));
    } catch { /* ignore */ }
  };

  if (loading) {
    return <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">VPN boshqaruvi</h1>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
          <Plus size={16} /> Yangi profil
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-200">
          <h2 className="font-semibold text-slate-800 flex items-center gap-2">
            <Globe size={16} className="text-indigo-500" /> VPN profillar
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">Nomi</th>
                <th className="text-left px-5 py-3 font-medium">Tur</th>
                <th className="text-left px-5 py-3 font-medium">Server manzili</th>
                <th className="text-left px-5 py-3 font-medium">Port</th>
                <th className="text-left px-5 py-3 font-medium">Holat</th>
                <th className="text-center px-5 py-3 font-medium">Mijozlar</th>
                <th className="text-right px-5 py-3 font-medium">Amallar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {profiles.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50">
                  <td className="px-5 py-4 font-medium text-slate-800">{p.name}</td>
                  <td className="px-5 py-4">
                    <span className="flex items-center gap-1.5 text-xs font-medium text-slate-600">
                      <Key size={12} className="text-slate-400" />
                      {p.type}
                    </span>
                  </td>
                  <td className="px-5 py-4 font-mono text-xs text-slate-600">{p.server_address}</td>
                  <td className="px-5 py-4 text-slate-600">{p.port}</td>
                  <td className="px-5 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge[p.status]}`}>{p.status}</span>
                  </td>
                  <td className="px-5 py-4 text-center">
                    <span className="flex items-center justify-center gap-1 text-sm">
                      <Users size={14} className="text-slate-400" />
                      {p.clients_count}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-right">
                    <button onClick={() => toggleStatus(p)}
                      className={`px-3 py-1.5 text-xs rounded-lg font-medium ${p.status === "active" ? "bg-amber-50 text-amber-600 hover:bg-amber-100" : "bg-emerald-50 text-emerald-600 hover:bg-emerald-100"}`}>
                      {p.status === "active" ? "O'chirish" : "Yoqish"}
                    </button>
                    <button onClick={() => handleDelete(p.id)} className="ml-2 p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg">
                      <X size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {profiles.length === 0 && <div className="text-center py-12 text-slate-400">Profillar mavjud emas</div>}
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-200">
          <h2 className="font-semibold text-slate-800 flex items-center gap-2">
            <Wifi size={16} className="text-emerald-500" /> Mening VPN mijozlarim
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">Mijoz nomi</th>
                <th className="text-left px-5 py-3 font-medium">Profil</th>
                <th className="text-left px-5 py-3 font-medium">IP manzil</th>
                <th className="text-left px-5 py-3 font-medium">Ulangan</th>
                <th className="text-right px-5 py-3 font-medium">Yuborilgan</th>
                <th className="text-right px-5 py-3 font-medium">Qabul qilingan</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {clients.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50">
                  <td className="px-5 py-4 font-medium text-slate-800">{c.client_name}</td>
                  <td className="px-5 py-4 text-slate-600">{c.profile_name}</td>
                  <td className="px-5 py-4 font-mono text-xs text-slate-600">{c.client_ip}</td>
                  <td className="px-5 py-4 text-xs text-slate-500">
                    {new Date(c.connected_since).toLocaleString("uz-UZ")}
                  </td>
                  <td className="px-5 py-4 text-right text-emerald-600 text-xs">
                    {formatBytes(c.bytes_sent)}
                  </td>
                  <td className="px-5 py-4 text-right text-blue-600 text-xs">
                    {formatBytes(c.bytes_received)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {clients.length === 0 && <div className="text-center py-12 text-slate-400">Ulangan mijozlar mavjud emas</div>}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">Yangi VPN profil</h2>
              <button onClick={() => setShowModal(false)} className="p-1 text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Profil nomi</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Tur</label>
                  <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="wireguard">WireGuard</option>
                    <option value="openvpn">OpenVPN</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Port</label>
                  <input type="number" value={form.port} onChange={(e) => setForm({ ...form, port: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Server manzili</label>
                <input type="text" value={form.server_address} onChange={(e) => setForm({ ...form, server_address: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="masalan: vpn.example.com" />
              </div>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Bekor qilish</button>
              <button onClick={handleCreate} className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Yaratish</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}
