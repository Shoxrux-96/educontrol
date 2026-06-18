import { useState, useEffect } from "react";
import { Plus, Edit3, Trash2, Search, X, RefreshCw } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface IPAddress {
  id: string;
  ip_address: string;
  mac_address?: string;
  hostname?: string;
  vendor?: string;
  is_dhcp: boolean;
  is_static: boolean;
  status: string;
  conflict?: boolean;
  last_seen?: string;
}

interface IPForm {
  ip_address: string;
  mac_address: string;
  hostname: string;
  vendor: string;
  is_dhcp: boolean;
  is_static: boolean;
}

const emptyForm: IPForm = {
  ip_address: "", mac_address: "", hostname: "", vendor: "",
  is_dhcp: false, is_static: false,
};

const tabs = ["Barcha IP lar", "DHCP Monitoring", "Konfliktlar", "Bo'sh IP lar"];

const statusBadge = (status: string) => {
  const m: Record<string, string> = {
    active: "bg-emerald-100 text-emerald-700",
    inactive: "bg-slate-100 text-slate-500",
    conflict: "bg-rose-100 text-rose-700",
  };
  return m[status] || "bg-slate-100 text-slate-500";
};

export default function IpManagement() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [ips, setIps] = useState<IPAddress[]>([]);
  const [freeIps, setFreeIps] = useState<string[]>([]);
  const [conflicts, setConflicts] = useState<IPAddress[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<IPAddress | null>(null);
  const [form, setForm] = useState<IPForm>(emptyForm);
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    if (activeTab === 0) fetchIps();
    else if (activeTab === 1) fetchIps("dhcp");
    else if (activeTab === 2) fetchConflicts();
    else if (activeTab === 3) fetchFreeIps();
  }, [activeTab]);

  const fetchIps = async (filter?: string) => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (search) params.search = search;
      if (filter === "dhcp") params.is_dhcp = "true";
      const { data } = await api.get<{ items: IPAddress[] }>("/network/ip-addresses", { params });
      setIps(data.items || []);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const fetchFreeIps = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<string[]>("/network/ip-addresses", { params: { free: "true" } });
      setFreeIps(Array.isArray(data) ? data : []);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const fetchConflicts = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<IPAddress[]>("/network/ip-addresses/conflicts");
      setConflicts(data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const scanConflicts = async () => {
    setScanning(true);
    try {
      await api.post("/network/ip-addresses/scan-conflicts");
      fetchConflicts();
    } catch { /* ignore */ }
    setScanning(false);
  };

  const openAdd = () => {
    setEditing(null);
    setForm(emptyForm);
    setShowModal(true);
  };

  const openEdit = (ip: IPAddress) => {
    setEditing(ip);
    setForm({
      ip_address: ip.ip_address,
      mac_address: ip.mac_address || "",
      hostname: ip.hostname || "",
      vendor: ip.vendor || "",
      is_dhcp: ip.is_dhcp,
      is_static: ip.is_static,
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    const payload = {
      ip_address: form.ip_address,
      mac_address: form.mac_address || undefined,
      hostname: form.hostname || undefined,
      vendor: form.vendor || undefined,
      is_dhcp: form.is_dhcp,
      is_static: form.is_static,
    };
    try {
      if (editing) {
        await api.patch(`/network/ip-addresses/${editing.id}`, payload);
      } else {
        await api.post("/network/ip-addresses", payload);
      }
      setShowModal(false);
      if (activeTab === 0) fetchIps();
      else if (activeTab === 1) fetchIps("dhcp");
    } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/network/ip-addresses/${id}`);
      setIps((prev) => prev.filter((ip) => ip.id !== id));
    } catch { /* ignore */ }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">IP Manzillar</h1>
        <div className="flex items-center gap-3">
          {activeTab < 2 && (
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text" value={search} onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") { if (activeTab === 0) fetchIps(); else fetchIps("dhcp"); } }}
                className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Qidirish..."
              />
            </div>
          )}
          {activeTab === 2 && (
            <button onClick={scanConflicts} disabled={scanning}
              className="flex items-center gap-2 px-4 py-2 bg-rose-600 text-white rounded-lg text-sm hover:bg-rose-700 disabled:opacity-50">
              <RefreshCw size={16} className={scanning ? "animate-spin" : ""} /> Scan Conflicts
            </button>
          )}
          {activeTab < 2 && (
            <button onClick={openAdd}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
              <Plus size={16} /> IP qo'shish
            </button>
          )}
        </div>
      </div>

      <div className="flex gap-1 mb-6 border-b border-slate-200">
        {tabs.map((tab, i) => (
          <button key={tab} onClick={() => setActiveTab(i)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === i
                ? "border-indigo-600 text-indigo-600"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}>
            {tab}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>
      ) : (
        <>
          {activeTab < 2 && (
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                      <th className="text-left px-4 py-3 font-medium">IP Address</th>
                      <th className="text-left px-4 py-3 font-medium">MAC Address</th>
                      <th className="text-left px-4 py-3 font-medium">Hostname</th>
                      <th className="text-left px-4 py-3 font-medium">Vendor</th>
                      <th className="text-left px-4 py-3 font-medium">Type</th>
                      <th className="text-left px-4 py-3 font-medium">Status</th>
                      <th className="text-left px-4 py-3 font-medium">Last Seen</th>
                      <th className="text-right px-4 py-3 font-medium">Amallar</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {ips.map((ip) => (
                      <tr key={ip.id} className="hover:bg-slate-50">
                        <td className="px-4 py-3 font-mono text-sm text-slate-800">{ip.ip_address}</td>
                        <td className="px-4 py-3 font-mono text-xs text-slate-600">{ip.mac_address || "—"}</td>
                        <td className="px-4 py-3 text-slate-600">{ip.hostname || "—"}</td>
                        <td className="px-4 py-3 text-slate-600">{ip.vendor || "—"}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            ip.is_dhcp ? "bg-blue-100 text-blue-700" : "bg-amber-100 text-amber-700"
                          }`}>
                            {ip.is_dhcp ? "DHCP" : "Static"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge(ip.status)}`}>
                            {ip.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-400">
                          {ip.last_seen ? new Date(ip.last_seen).toLocaleString("uz-UZ") : "—"}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button onClick={() => openEdit(ip)} className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg">
                            <Edit3 size={14} />
                          </button>
                          <button onClick={() => handleDelete(ip.id)} className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg ml-1">
                            <Trash2 size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {ips.length === 0 && <div className="text-center py-12 text-slate-400">IP manzillar mavjud emas</div>}
            </div>
          )}

          {activeTab === 2 && (
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                      <th className="text-left px-4 py-3 font-medium">IP Address</th>
                      <th className="text-left px-4 py-3 font-medium">MAC Address</th>
                      <th className="text-left px-4 py-3 font-medium">Hostname</th>
                      <th className="text-left px-4 py-3 font-medium">Vendor</th>
                      <th className="text-left px-4 py-3 font-medium">Type</th>
                      <th className="text-left px-4 py-3 font-medium">Status</th>
                      <th className="text-left px-4 py-3 font-medium">Last Seen</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {conflicts.map((ip) => (
                      <tr key={ip.id} className="hover:bg-slate-50">
                        <td className="px-4 py-3 font-mono text-sm text-slate-800">{ip.ip_address}</td>
                        <td className="px-4 py-3 font-mono text-xs text-slate-600">{ip.mac_address || "—"}</td>
                        <td className="px-4 py-3 text-slate-600">{ip.hostname || "—"}</td>
                        <td className="px-4 py-3 text-slate-600">{ip.vendor || "—"}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            ip.is_dhcp ? "bg-blue-100 text-blue-700" : "bg-amber-100 text-amber-700"
                          }`}>
                            {ip.is_dhcp ? "DHCP" : "Static"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge(ip.status)}`}>
                            {ip.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-400">
                          {ip.last_seen ? new Date(ip.last_seen).toLocaleString("uz-UZ") : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {conflicts.length === 0 && <div className="text-center py-12 text-slate-400">Konfliktlar mavjud emas</div>}
            </div>
          )}

          {activeTab === 3 && (
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <div className="p-4 border-b border-slate-100">
                <p className="text-sm text-slate-500">Bo'sh IP manzillar (192.168.1.0/24)</p>
              </div>
              <div className="flex flex-wrap gap-2 p-4">
                {freeIps.length === 0 ? (
                  <p className="text-sm text-slate-400 w-full text-center py-8">Bo'sh IP manzillar mavjud emas</p>
                ) : (
                  freeIps.map((ip) => (
                    <span key={ip}
                      className="px-3 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg text-sm font-mono">
                      {ip}
                    </span>
                  ))
                )}
              </div>
            </div>
          )}
        </>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">{editing ? "IP manzilni tahrirlash" : "Yangi IP manzil"}</h2>
              <button onClick={() => setShowModal(false)} className="p-1 text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            <div className="px-6 py-4 space-y-4">
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
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Hostname</label>
                <input type="text" value={form.hostname} onChange={(e) => setForm({ ...form, hostname: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Vendor</label>
                <input type="text" value={form.vendor} onChange={(e) => setForm({ ...form, vendor: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div className="flex gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.is_dhcp} onChange={(e) => setForm({ ...form, is_dhcp: e.target.checked })}
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                  <span className="text-sm text-slate-600">DHCP</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.is_static} onChange={(e) => setForm({ ...form, is_static: e.target.checked })}
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                  <span className="text-sm text-slate-600">Static</span>
                </label>
              </div>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Bekor qilish</button>
              <button onClick={handleSave} className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                {editing ? "Saqlash" : "Qo'shish"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
