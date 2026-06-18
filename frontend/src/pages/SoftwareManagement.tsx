import { useState, useEffect } from "react";
import { Package, Server, Upload, CheckCircle, XCircle, Clock, Search, Plus, Pencil, Trash2, Monitor, RefreshCw, X } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";
import type { Computer } from "../types";

interface SoftwareItem {
  id: string;
  name: string;
  version?: string;
  publisher?: string;
  install_date?: string;
  size_mb?: number;
  computers_count?: number;
}

interface SoftwarePackage {
  id: string;
  name: string;
  display_name?: string;
  package_type: string;
  description?: string;
  installer_path?: string;
  installer_url?: string;
  installer_args?: string;
  checksum?: string;
  size_mb?: number;
  is_active: boolean;
  created_at: string;
}

interface Deployment {
  id: string;
  name?: string;
  package_name?: string;
  package_id: string;
  target_type: string;
  target_ids?: string[];
  status: string;
  total_count: number;
  completed_count: number;
  failed_count: number;
  created_at: string;
}

interface PackageForm {
  name: string;
  display_name: string;
  description: string;
  package_type: string;
  installer_path: string;
  installer_url: string;
  installer_args: string;
  checksum: string;
  size_mb: string;
  is_active: boolean;
}

const emptyPackageForm: PackageForm = {
  name: "", display_name: "", description: "", package_type: "msi",
  installer_path: "", installer_url: "", installer_args: "", checksum: "",
  size_mb: "0", is_active: true,
};

const tabs = [
  { key: "inventory", label: "Dasturiy ta'minot inventarizatsiyasi", icon: Server },
  { key: "packages", label: "Paketlar", icon: Package },
  { key: "deploy", label: "O'rnatish", icon: Upload },
];

export default function SoftwareManagement() {
  useAuth();
  const [activeTab, setActiveTab] = useState("inventory");

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Dasturiy ta'minot boshqaruvi</h1>
      </div>

      <div className="flex gap-1 mb-6 bg-slate-100 p-1 rounded-lg w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === t.key ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <t.icon size={16} />
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "inventory" && <SoftwareInventory />}
      {activeTab === "packages" && <SoftwarePackages />}
      {activeTab === "deploy" && <Deployment />}
    </div>
  );
}

function SoftwareInventory() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SoftwareItem[]>([]);
  const [computers, setComputers] = useState<Computer[]>([]);
  const [selectedComputerId, setSelectedComputerId] = useState("");
  const [installedSoftware, setInstalledSoftware] = useState<SoftwareItem[]>([]);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    api.get<{ items: Computer[] }>("/computers?page_size=100").then((r) => {
      setComputers(r.data.items || []);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!query.trim()) { setResults([]); return; }
    const t = setTimeout(() => {
      api.get<SoftwareItem[]>(`/computers/software/search?q=${encodeURIComponent(query)}`).then((r) => {
        setResults(Array.isArray(r.data) ? r.data : []);
      }).catch(() => {});
    }, 300);
    return () => clearTimeout(t);
  }, [query]);

  useEffect(() => {
    if (!selectedComputerId) { setInstalledSoftware([]); return; }
    api.get<SoftwareItem[]>(`/computers/${selectedComputerId}/software`).then((r) => {
      setInstalledSoftware(Array.isArray(r.data) ? r.data : []);
    }).catch(() => {});
  }, [selectedComputerId]);

  const handleSync = async () => {
    if (!selectedComputerId) return;
    setSyncing(true);
    try {
      await api.post(`/computers/${selectedComputerId}/software/sync`);
      const r = await api.get<SoftwareItem[]>(`/computers/${selectedComputerId}/software`);
      setInstalledSoftware(Array.isArray(r.data) ? r.data : []);
    } catch { /* ignore */ }
    setSyncing(false);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-200">
          <h2 className="font-semibold text-slate-800 flex items-center gap-2">
            <Search size={16} className="text-indigo-500" /> Dasturiy ta'minot qidirish
          </h2>
        </div>
        <div className="p-5">
          <div className="relative max-w-md">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text" value={query} onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Dastur nomi bo'yicha qidirish..."
            />
          </div>
          {results.length > 0 && (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                    <th className="text-left px-4 py-2 font-medium">Dastur nomi</th>
                    <th className="text-right px-4 py-2 font-medium">Kompyuterlar soni</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {results.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-800">{r.name}</td>
                      <td className="px-4 py-3 text-right text-slate-600">{r.computers_count ?? 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="font-semibold text-slate-800 flex items-center gap-2">
            <Monitor size={16} className="text-indigo-500" /> Kompyuter dasturlari
          </h2>
          <div className="flex items-center gap-3">
            <select
              value={selectedComputerId}
              onChange={(e) => setSelectedComputerId(e.target.value)}
              className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Kompyuterni tanlang</option>
              {computers.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
            <button
              onClick={handleSync}
              disabled={!selectedComputerId || syncing}
              className="flex items-center gap-1.5 px-3 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              <RefreshCw size={14} className={syncing ? "animate-spin" : ""} />
              Sync
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">Nomi</th>
                <th className="text-left px-5 py-3 font-medium">Versiya</th>
                <th className="text-left px-5 py-3 font-medium">Nashriyotchi</th>
                <th className="text-left px-5 py-3 font-medium">O'rnatilgan sana</th>
                <th className="text-right px-5 py-3 font-medium">Hajmi (MB)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {installedSoftware.map((s, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="px-5 py-3 font-medium text-slate-800">{s.name}</td>
                  <td className="px-5 py-3 text-slate-600">{s.version || "-"}</td>
                  <td className="px-5 py-3 text-slate-600">{s.publisher || "-"}</td>
                  <td className="px-5 py-3 text-slate-600">{s.install_date ? new Date(s.install_date).toLocaleDateString("uz-UZ") : "-"}</td>
                  <td className="px-5 py-3 text-right text-slate-600">{s.size_mb ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!selectedComputerId && <div className="text-center py-12 text-slate-400">Kompyuterni tanlang</div>}
        {selectedComputerId && installedSoftware.length === 0 && <div className="text-center py-12 text-slate-400">Dasturlar topilmadi</div>}
      </div>
    </div>
  );
}

function SoftwarePackages() {
  const { isAdmin } = useAuth();
  const [packages, setPackages] = useState<SoftwarePackage[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<PackageForm>(emptyPackageForm);

  useEffect(() => { fetchPackages(); }, []);

  const fetchPackages = async () => {
    try {
      const r = await api.get<SoftwarePackage[]>("/computers/software/packages");
      setPackages(Array.isArray(r.data) ? r.data : []);
    } catch { /* ignore */ }
  };

  const openNew = () => {
    setForm(emptyPackageForm);
    setEditingId(null);
    setShowModal(true);
  };

  const openEdit = (p: SoftwarePackage) => {
    setForm({
      name: p.name,
      display_name: p.display_name || "",
      description: p.description || "",
      package_type: p.package_type,
      installer_path: p.installer_path || "",
      installer_url: p.installer_url || "",
      installer_args: p.installer_args || "",
      checksum: p.checksum || "",
      size_mb: String(p.size_mb ?? 0),
      is_active: p.is_active,
    });
    setEditingId(p.id);
    setShowModal(true);
  };

  const handleSave = async () => {
    const payload = {
      ...form,
      size_mb: form.size_mb ? Number(form.size_mb) : 0,
    };
    try {
      if (editingId) {
        await api.patch(`/computers/software/packages/${editingId}`, payload);
      } else {
        await api.post("/computers/software/packages", payload);
      }
      setShowModal(false);
      fetchPackages();
    } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/computers/software/packages/${id}`);
      fetchPackages();
    } catch { /* ignore */ }
  };

  const typeBadge: Record<string, string> = {
    msi: "bg-blue-100 text-blue-700",
    exe: "bg-violet-100 text-violet-700",
    msu: "bg-amber-100 text-amber-700",
    script: "bg-emerald-100 text-emerald-700",
    custom: "bg-slate-100 text-slate-600",
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-slate-800">Paketlar ro'yxati</h2>
        {isAdmin && (
          <button onClick={openNew} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
            <Plus size={16} /> Yangi paket
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
              <th className="text-left px-5 py-3 font-medium">Nomi</th>
              <th className="text-left px-5 py-3 font-medium">Ko'rinadigan nom</th>
              <th className="text-left px-5 py-3 font-medium">Tur</th>
              <th className="text-right px-5 py-3 font-medium">Hajmi</th>
              <th className="text-left px-5 py-3 font-medium">Holat</th>
              <th className="text-right px-5 py-3 font-medium">Amallar</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {packages.map((p) => (
              <tr key={p.id} className="hover:bg-slate-50">
                <td className="px-5 py-3 font-medium text-slate-800">{p.name}</td>
                <td className="px-5 py-3 text-slate-600">{p.display_name || "-"}</td>
                <td className="px-5 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${typeBadge[p.package_type] || typeBadge.custom}`}>
                    {p.package_type}
                  </span>
                </td>
                <td className="px-5 py-3 text-right text-slate-600">{p.size_mb ? `${p.size_mb} MB` : "-"}</td>
                <td className="px-5 py-3">
                  {p.is_active
                    ? <span className="flex items-center gap-1 text-xs text-emerald-600"><CheckCircle size={12} /> Active</span>
                    : <span className="flex items-center gap-1 text-xs text-slate-400"><XCircle size={12} /> Inactive</span>
                  }
                </td>
                <td className="px-5 py-3 text-right">
                  {isAdmin && (
                    <>
                      <button onClick={() => openEdit(p)} className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg">
                        <Pencil size={14} />
                      </button>
                      <button onClick={() => handleDelete(p.id)} className="ml-1 p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg">
                        <Trash2 size={14} />
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {packages.length === 0 && <div className="text-center py-12 text-slate-400">Paketlar mavjud emas</div>}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">{editingId ? "Paketni tahrirlash" : "Yangi paket"}</h2>
              <button onClick={() => setShowModal(false)} className="p-1 text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Nomi *</label>
                  <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Ko'rinadigan nom</label>
                  <input type="text" value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Tavsif</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" rows={2} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Paket turi</label>
                  <select value={form.package_type} onChange={(e) => setForm({ ...form, package_type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="msi">MSI</option>
                    <option value="exe">EXE</option>
                    <option value="msu">MSU</option>
                    <option value="script">Script</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Hajmi (MB)</label>
                  <input type="number" value={form.size_mb} onChange={(e) => setForm({ ...form, size_mb: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Installer yo'li</label>
                <input type="text" value={form.installer_path} onChange={(e) => setForm({ ...form, installer_path: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="\\\\server\\share\\installer.msi" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Installer URL</label>
                <input type="text" value={form.installer_url} onChange={(e) => setForm({ ...form, installer_url: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="https://example.com/installer.msi" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Installer argumentlari</label>
                  <input type="text" value={form.installer_args} onChange={(e) => setForm({ ...form, installer_args: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="/quiet /norestart" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Checksum</label>
                  <input type="text" value={form.checksum} onChange={(e) => setForm({ ...form, checksum: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="is_active" checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                <label htmlFor="is_active" className="text-sm text-slate-700">Aktiv</label>
              </div>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Bekor qilish</button>
              <button onClick={handleSave} className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                {editingId ? "Saqlash" : "Yaratish"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Deployment() {
  const [packages, setPackages] = useState<SoftwarePackage[]>([]);
  const [computers, setComputers] = useState<Computer[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [selectedPackageId, setSelectedPackageId] = useState("");
  const [targetType, setTargetType] = useState<"computer" | "group" | "all">("computer");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(false);
  const [deploying, setDeploying] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get<SoftwarePackage[]>("/computers/software/packages"),
      api.get<{ items: Computer[] }>("/computers?page_size=200"),
      api.get<Deployment[]>("/computers/deployments"),
    ]).then(([p, c, d]) => {
      setPackages(Array.isArray(p.data) ? p.data : []);
      setComputers(c.data.items || []);
      setDeployments(Array.isArray(d.data) ? d.data : []);
    }).catch(() => {});
  }, []);

  const handleSelectAll = (checked: boolean) => {
    setSelectAll(checked);
    if (checked) {
      setSelectedIds(computers.map((c) => c.id));
      setTargetType("all");
    } else {
      setSelectedIds([]);
      setTargetType("computer");
    }
  };

  const toggleComputer = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
    setSelectAll(false);
    setTargetType("computer");
  };

  const filteredComputers = computers.filter((c) => c.status === "online");

  const handleDeploy = async () => {
    if (!selectedPackageId) return;
    setDeploying(true);
    const payload = {
      package_id: selectedPackageId,
      target_type: targetType,
      target_ids: targetType === "all" ? [] : selectedIds,
    };
    try {
      await api.post("/computers/deployments", payload);
      setSelectedPackageId("");
      setSelectedIds([]);
      setSelectAll(false);
      setTargetType("computer");
      const r = await api.get<Deployment[]>("/computers/deployments");
      setDeployments(Array.isArray(r.data) ? r.data : []);
    } catch { /* ignore */ }
    setDeploying(false);
  };

  const deployCount = targetType === "all" ? computers.length : selectedIds.length;

  const statusBadge: Record<string, string> = {
    pending: "bg-amber-100 text-amber-700",
    running: "bg-blue-100 text-blue-700",
    completed: "bg-emerald-100 text-emerald-700",
    failed: "bg-rose-100 text-rose-700",
    cancelled: "bg-slate-100 text-slate-500",
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <h2 className="font-semibold text-slate-800 mb-4">Yangi o'rnatish</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">1-qadam: Paketni tanlang</label>
            <select value={selectedPackageId} onChange={(e) => setSelectedPackageId(e.target.value)}
              className="w-full max-w-md px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="">Paketni tanlang</option>
              {packages.filter((p) => p.is_active).map((p) => (
                <option key={p.id} value={p.id}>{p.display_name || p.name} ({p.package_type})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">2-qadam: Maqsadni tanlang</label>
            <div className="flex items-center gap-4 mb-3">
              <label className="flex items-center gap-1.5 text-sm">
                <input type="checkbox" checked={selectAll} onChange={(e) => handleSelectAll(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                Barcha kompyuterlar ({computers.length} ta)
              </label>
            </div>
            {!selectAll && (
              <div className="max-h-40 overflow-y-auto border border-slate-200 rounded-lg p-2 space-y-1">
                {filteredComputers.map((c) => (
                  <label key={c.id} className="flex items-center gap-2 px-2 py-1 hover:bg-slate-50 rounded cursor-pointer text-sm">
                    <input type="checkbox" checked={selectedIds.includes(c.id)}
                      onChange={() => toggleComputer(c.id)}
                      className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                    {c.name}
                    <span className="text-xs text-slate-400 ml-auto">{c.ip_address}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {selectedPackageId && deployCount > 0 && (
            <p className="text-sm text-slate-600">
              {deployCount} ta kompyuterga o'rnatilmoqda
            </p>
          )}

          <button onClick={handleDeploy} disabled={!selectedPackageId || deployCount === 0 || deploying}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
            <Upload size={16} />
            {deploying ? "O'rnatilmoqda..." : "O'rnatish"}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-200">
          <h2 className="font-semibold text-slate-800 flex items-center gap-2">
            <Clock size={16} className="text-slate-400" /> O'rnatish tarixi
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">Nomi</th>
                <th className="text-left px-5 py-3 font-medium">Paket</th>
                <th className="text-left px-5 py-3 font-medium">Maqsad turi</th>
                <th className="text-left px-5 py-3 font-medium">Holat</th>
                <th className="text-center px-5 py-3 font-medium">Jami</th>
                <th className="text-center px-5 py-3 font-medium">Bajarilgan</th>
                <th className="text-center px-5 py-3 font-medium">Xatolik</th>
                <th className="text-right px-5 py-3 font-medium">Sana</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {deployments.map((d) => (
                <tr key={d.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3 font-medium text-slate-800">{d.name || "-"}</td>
                  <td className="px-5 py-3 text-slate-600">{d.package_name || d.package_id}</td>
                  <td className="px-5 py-3 text-slate-600">{d.target_type}</td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge[d.status] || statusBadge.pending}`}>
                      {d.status}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-center text-slate-600">{d.total_count}</td>
                  <td className="px-5 py-3 text-center text-emerald-600">{d.completed_count}</td>
                  <td className="px-5 py-3 text-center text-rose-600">{d.failed_count}</td>
                  <td className="px-5 py-3 text-right text-xs text-slate-500">
                    {new Date(d.created_at).toLocaleString("uz-UZ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {deployments.length === 0 && <div className="text-center py-12 text-slate-400">O'rnatishlar mavjud emas</div>}
      </div>
    </div>
  );
}
