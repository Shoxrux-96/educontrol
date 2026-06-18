import { useState, useEffect } from "react";
import {
  ZapOff, Settings, Terminal, FileJson, Plus, Pencil, Trash2, Search, X, Loader2,
  AlertTriangle, Shield, Target, Globe, Monitor, Users, CheckCircle, Sliders
} from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface Gpo {
  id: string;
  name: string;
  description?: string;
  target_type: "all" | "user" | "computer" | "group";
  target_id?: string;
  usb_block: boolean;
  control_panel_block: boolean;
  cmd_block: boolean;
  registry_block: boolean;
  apply_to_computers: boolean;
  apply_to_users: boolean;
  is_active: boolean;
  settings?: Record<string, any>;
  created_at: string;
}

interface GpoForm {
  name: string;
  description: string;
  target_type: string;
  target_id: string;
  usb_block: boolean;
  control_panel_block: boolean;
  cmd_block: boolean;
  registry_block: boolean;
  apply_to_computers: boolean;
  apply_to_users: boolean;
  is_active: boolean;
  settings: string;
}

const emptyForm: GpoForm = {
  name: "", description: "", target_type: "all", target_id: "",
  usb_block: false, control_panel_block: false, cmd_block: false, registry_block: false,
  apply_to_computers: false, apply_to_users: false, is_active: true,
  settings: "{}",
};

const POLICY_CARDS = [
  { key: "usb_block", icon: ZapOff, title: "USB bloklash", desc: "Fleshka, tashqi disklar va USB qurilmalarni bloklash", color: "rose" },
  { key: "control_panel_block", icon: Settings, title: "Control Panel bloklash", desc: "Boshqarish paneli va sozlamalarga kirishni bloklash", color: "amber" },
  { key: "cmd_block", icon: Terminal, title: "CMD bloklash", desc: "Buyruqlar satri (cmd.exe) va PowerShell ni bloklash", color: "violet" },
  { key: "registry_block", icon: FileJson, title: "Registry bloklash", desc: "Registry muharriri (regedit) ni bloklash", color: "cyan" },
];

const TARGET_OPTIONS = [
  { value: "all", label: "Hamma qurilmalar", icon: Globe },
  { value: "computer", label: "Kompyuter", icon: Monitor },
  { value: "group", label: "Guruh", icon: Users },
  { value: "user", label: "Foydalanuvchi", icon: Users },
];

type TabName = "asosiy" | "bloklash" | "qollash";

const TABS: { key: TabName; label: string; icon: any }[] = [
  { key: "asosiy", label: "Asosiy", icon: Sliders },
  { key: "bloklash", label: "Bloklashlar", icon: Shield },
  { key: "qollash", label: "Qo'llash", icon: Target },
];

export default function GroupPolicy() {
  const { user } = useAuth();
  const canModify = user?.role === "owner" || user?.role === "admin";
  const [gpos, setGpos] = useState<Gpo[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Gpo | null>(null);
  const [form, setForm] = useState<GpoForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<TabName>("asosiy");
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [cardStates, setCardStates] = useState<Record<string, boolean>>({});

  useEffect(() => { fetchGpos(); }, []);

  const fetchGpos = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<Gpo[]>("/ad/gpos");
      setGpos(Array.isArray(data) ? data : []);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const applyPolicy = async (key: string) => {
    const enabled = !cardStates[key];
    setCardStates((prev) => ({ ...prev, [key]: enabled }));
    try {
      await api.post("/ad/gpos", {
        name: POLICY_CARDS.find((c) => c.key === key)!.title,
        target_type: "all",
        [key]: enabled,
        is_active: true,
      });
      fetchGpos();
    } catch { /* ignore */ }
  };

  const openAdd = () => {
    setEditing(null);
    setForm(emptyForm);
    setActiveTab("asosiy");
    setError("");
    setShowModal(true);
  };

  const openEdit = (gpo: Gpo) => {
    setEditing(gpo);
    setForm({
      name: gpo.name,
      description: gpo.description || "",
      target_type: gpo.target_type,
      target_id: gpo.target_id || "",
      usb_block: gpo.usb_block,
      control_panel_block: gpo.control_panel_block,
      cmd_block: gpo.cmd_block,
      registry_block: gpo.registry_block,
      apply_to_computers: gpo.apply_to_computers,
      apply_to_users: gpo.apply_to_users,
      is_active: gpo.is_active,
      settings: gpo.settings ? JSON.stringify(gpo.settings, null, 2) : "{}",
    });
    setActiveTab("asosiy");
    setError("");
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) return;
    setShowModal(false);
    setEditing(null);
    setForm(emptyForm);
    setError("");
    setActiveTab("asosiy");
  };

  const validate = () => {
    if (!form.name.trim()) {
      setError("Siyosat nomini kiriting");
      return false;
    }
    try {
      const parsed = JSON.parse(form.settings);
      if (typeof parsed !== "object" || Array.isArray(parsed)) {
        setError("Settings: JSON obyekt bo'lishi kerak");
        return false;
      }
    } catch {
      setError("Settings: noto'g'ri JSON format");
      return false;
    }
    return true;
  };

  const handleSave = async () => {
    if (!validate()) return;
    setSaving(true);
    setError("");
    try {
      const payload = {
        name: form.name,
        description: form.description || undefined,
        target_type: form.target_type,
        target_id: form.target_id || undefined,
        usb_block: form.usb_block,
        control_panel_block: form.control_panel_block,
        cmd_block: form.cmd_block,
        registry_block: form.registry_block,
        apply_to_computers: form.apply_to_computers,
        apply_to_users: form.apply_to_users,
        is_active: form.is_active,
        settings: JSON.parse(form.settings),
      };
      if (editing) {
        await api.patch(`/ad/gpos/${editing.id}`, payload);
      } else {
        await api.post("/ad/gpos", payload);
      }
      closeModal();
      fetchGpos();
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Saqlashda xatolik yuz berdi");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    setDeleting(true);
    try {
      await api.delete(`/ad/gpos/${id}`);
      setDeleteConfirm(null);
      fetchGpos();
    } catch {
      setError("O'chirishda xatolik yuz berdi");
    } finally {
      setDeleting(false);
    }
  };

  const toggleStatus = async (gpo: Gpo) => {
    try {
      await api.patch(`/ad/gpos/${gpo.id}`, { is_active: !gpo.is_active });
      setGpos((prev) => prev.map((g) => g.id === gpo.id ? { ...g, is_active: !g.is_active } : g));
    } catch { /* ignore */ }
  };

  const filtered = gpos.filter((g) =>
    g.name.toLowerCase().includes(search.toLowerCase())
  );

  const targetLabel = (t: string) => {
    const m: Record<string, string> = { all: "Hamma", user: "Foydalanuvchi", computer: "Kompyuter", group: "Guruh" };
    return m[t] || t;
  };

  const Toggle = ({ checked, onChange, disabled }: { checked: boolean; onChange: () => void; disabled?: boolean }) => (
    <button
      type="button"
      onClick={onChange}
      disabled={disabled}
      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
        disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
      } ${checked ? "bg-emerald-500" : "bg-slate-300"}`}
    >
      <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
        checked ? "translate-x-[18px]" : "translate-x-1"
      }`} />
    </button>
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Group Policy</h1>
          <p className="text-sm text-slate-500 mt-0.5">{gpos.length} ta siyosat</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 w-56"
              placeholder="Qidirish..." />
          </div>
          {canModify && (
            <button onClick={openAdd}
              className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm">
              <Plus size={16} /> Yangi siyosat
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        {POLICY_CARDS.map(({ key, icon: Icon, title, desc }) => (
          <div key={key} className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                key === "usb_block" ? "bg-rose-50" :
                key === "control_panel_block" ? "bg-amber-50" :
                key === "cmd_block" ? "bg-violet-50" : "bg-cyan-50"
              }`}>
                <Icon size={20} className={`${
                  key === "usb_block" ? "text-rose-600" :
                  key === "control_panel_block" ? "text-amber-600" :
                  key === "cmd_block" ? "text-violet-600" : "text-cyan-600"
                }`} />
              </div>
              <Toggle checked={cardStates[key]} onChange={() => applyPolicy(key)} />
            </div>
            <h3 className="font-semibold text-slate-800 mb-1">{title}</h3>
            <p className="text-sm text-slate-500 mb-3">{desc}</p>
            <div className="flex items-center justify-between">
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                cardStates[key]
                  ? "bg-emerald-100 text-emerald-700"
                  : "bg-slate-100 text-slate-500"
              }`}>
                {cardStates[key] ? "Faol" : "No faol"}
              </span>
              <button onClick={() => applyPolicy(key)}
                className="px-3 py-1.5 text-xs bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                Qo'llash
              </button>
            </div>
          </div>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 size={24} className="text-indigo-500 animate-spin" />
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                  <th className="text-left px-4 py-3 font-medium">Nomi</th>
                  <th className="text-left px-4 py-3 font-medium">Target</th>
                  <th className="text-center px-4 py-3 font-medium">USB</th>
                  <th className="text-center px-4 py-3 font-medium">CP</th>
                  <th className="text-center px-4 py-3 font-medium">CMD</th>
                  <th className="text-center px-4 py-3 font-medium">Registry</th>
                  <th className="text-center px-4 py-3 font-medium">Holat</th>
                  <th className="text-left px-4 py-3 font-medium">Yaratilgan</th>
                  <th className="text-right px-4 py-3 font-medium">Amallar</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((g) => (
                  <tr key={g.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <span className="font-medium text-slate-800">{g.name}</span>
                      {g.description && <p className="text-xs text-slate-400 truncate max-w-[200px]">{g.description}</p>}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs font-medium px-2 py-1 rounded-full bg-slate-100 text-slate-600">
                        {targetLabel(g.target_type)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {g.usb_block
                        ? <span className="text-emerald-500 text-xs font-bold bg-emerald-50 px-2 py-1 rounded-full">✓</span>
                        : <span className="text-slate-300">—</span>}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {g.control_panel_block
                        ? <span className="text-emerald-500 text-xs font-bold bg-emerald-50 px-2 py-1 rounded-full">✓</span>
                        : <span className="text-slate-300">—</span>}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {g.cmd_block
                        ? <span className="text-emerald-500 text-xs font-bold bg-emerald-50 px-2 py-1 rounded-full">✓</span>
                        : <span className="text-slate-300">—</span>}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {g.registry_block
                        ? <span className="text-emerald-500 text-xs font-bold bg-emerald-50 px-2 py-1 rounded-full">✓</span>
                        : <span className="text-slate-300">—</span>}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Toggle checked={g.is_active} onChange={() => toggleStatus(g)} />
                    </td>
                    <td className="px-4 py-3 text-slate-500 text-xs whitespace-nowrap">
                      {new Date(g.created_at).toLocaleString("uz-UZ")}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => openEdit(g)}
                          className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                          title="Tahrirlash">
                          <Pencil size={14} />
                        </button>
                        <button onClick={() => setDeleteConfirm(g.id)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                          title="O'chirish">
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filtered.length === 0 && (
            <div className="text-center py-16">
              <Shield size={40} className="mx-auto text-slate-300 mb-3" />
              <p className="text-slate-400 mb-4">Siyosat topilmadi</p>
              {canModify && (
                <button onClick={openAdd}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors">
                  <Plus size={16} /> Birinchi siyosatni yaratish
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Delete confirmation modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 p-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-rose-50 flex items-center justify-center">
              <AlertTriangle size={24} className="text-rose-500" />
            </div>
            <h3 className="text-lg font-bold text-slate-800 mb-2">Siyosatni o'chirish</h3>
            <p className="text-sm text-slate-500 mb-6">Bu siyosatni o'chirishni tasdiqlaysizmi? Bu amalni qaytarib bo'lmaydi.</p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                disabled={deleting}
              >
                Bekor qilish
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="px-4 py-2.5 text-sm font-medium bg-rose-600 text-white rounded-lg hover:bg-rose-700 transition-colors flex items-center gap-2"
                disabled={deleting}
              >
                {deleting ? <Loader2 size={15} className="animate-spin" /> : <Trash2 size={15} />}
                {deleting ? "O'chirilmoqda..." : "O'chirish"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={closeModal}>
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-5 border-b border-slate-100">
              <div>
                <h2 className="text-lg font-bold text-slate-800">
                  {editing ? "Siyosatni tahrirlash" : "Yangi siyosat"}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  {editing ? "Siyosat sozlamalarini yangilang" : "Kompyuterlar uchun yangi siyosat yarating"}
                </p>
              </div>
              <button onClick={closeModal}
                className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
                <X size={18} />
              </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-100 bg-slate-50/50">
              {TABS.map(({ key, label, icon: Icon }) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key)}
                  className={`flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === key
                      ? "border-indigo-600 text-indigo-600 bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-700"
                  }`}
                >
                  <Icon size={15} />
                  {label}
                </button>
              ))}
            </div>

            <div className="p-5 max-h-[60vh] overflow-y-auto space-y-5">
              {error && (
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-sm text-rose-700 flex items-center gap-2">
                  <AlertTriangle size={15} /> {error}
                  <button onClick={() => setError("")} className="ml-auto text-rose-400 hover:text-rose-600"><X size={14} /></button>
                </div>
              )}

              {/* Tab 1: Asosiy */}
              {activeTab === "asosiy" && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                      Siyosat nomi <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={form.name}
                      onChange={(e) => { setForm({ ...form, name: e.target.value }); setError(""); }}
                      className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow"
                      placeholder="Masalan: USB bloklash, CMD cheklash"
                      autoFocus
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Tavsif</label>
                    <textarea
                      value={form.description}
                      onChange={(e) => setForm({ ...form, description: e.target.value })}
                      className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow resize-none"
                      rows={3}
                      placeholder="Siyosat haqida qisqacha ma'lumot"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Qo'llaniladigan qurilmalar</label>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      {TARGET_OPTIONS.map(({ value, label, icon: Icon }) => (
                        <button
                          key={value}
                          onClick={() => setForm({ ...form, target_type: value, target_id: value === "all" ? "" : form.target_id })}
                          className={`flex flex-col items-center gap-2 px-3 py-3 rounded-xl border-2 transition-all ${
                            form.target_type === value
                              ? "border-indigo-500 bg-indigo-50 text-indigo-700 ring-1 ring-indigo-500"
                              : "border-slate-200 text-slate-500 hover:border-slate-300"
                          }`}
                        >
                          <Icon size={20} />
                          <span className="text-xs font-medium">{label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  {form.target_type !== "all" && (
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        {form.target_type === "group" ? "Guruh ID" :
                         form.target_type === "computer" ? "Kompyuter ID" : "Foydalanuvchi ID"}
                      </label>
                      <input
                        type="text"
                        value={form.target_id}
                        onChange={(e) => setForm({ ...form, target_id: e.target.value })}
                        className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow"
                        placeholder="ID ni kiriting"
                      />
                    </div>
                  )}
                </>
              )}

              {/* Tab 2: Bloklashlar */}
              {activeTab === "bloklash" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-rose-200 hover:bg-rose-50/30 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-rose-50 flex items-center justify-center">
                        <ZapOff size={20} className="text-rose-600" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">USB bloklash</p>
                        <p className="text-xs text-slate-500">Fleshka, tashqi disklar va USB qurilmalarni bloklash</p>
                      </div>
                    </div>
                    <Toggle checked={form.usb_block} onChange={() => setForm({ ...form, usb_block: !form.usb_block })} />
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-amber-200 hover:bg-amber-50/30 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
                        <Settings size={20} className="text-amber-600" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">Control Panel bloklash</p>
                        <p className="text-xs text-slate-500">Boshqarish paneli va tizim sozlamalariga kirishni bloklash</p>
                      </div>
                    </div>
                    <Toggle checked={form.control_panel_block} onChange={() => setForm({ ...form, control_panel_block: !form.control_panel_block })} />
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-violet-200 hover:bg-violet-50/30 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-violet-50 flex items-center justify-center">
                        <Terminal size={20} className="text-violet-600" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">CMD bloklash</p>
                        <p className="text-xs text-slate-500">Buyruqlar satri (cmd.exe) va PowerShell ni bloklash</p>
                      </div>
                    </div>
                    <Toggle checked={form.cmd_block} onChange={() => setForm({ ...form, cmd_block: !form.cmd_block })} />
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-cyan-200 hover:bg-cyan-50/30 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-cyan-50 flex items-center justify-center">
                        <FileJson size={20} className="text-cyan-600" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">Registry bloklash</p>
                        <p className="text-xs text-slate-500">Registry muharriri (regedit) ni bloklash</p>
                      </div>
                    </div>
                    <Toggle checked={form.registry_block} onChange={() => setForm({ ...form, registry_block: !form.registry_block })} />
                  </div>
                </div>
              )}

              {/* Tab 3: Qo'llash */}
              {activeTab === "qollash" && (
                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-3">Qo'llash sozlamalari</label>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
                        <div className="flex items-center gap-2">
                          <Monitor size={16} className="text-slate-500" />
                          <span className="text-sm text-slate-700">Kompyuterlarga qo'llash</span>
                        </div>
                        <Toggle checked={form.apply_to_computers} onChange={() => setForm({ ...form, apply_to_computers: !form.apply_to_computers })} />
                      </div>
                      <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
                        <div className="flex items-center gap-2">
                          <Users size={16} className="text-slate-500" />
                          <span className="text-sm text-slate-700">Foydalanuvchilarga qo'llash</span>
                        </div>
                        <Toggle checked={form.apply_to_users} onChange={() => setForm({ ...form, apply_to_users: !form.apply_to_users })} />
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-xl border border-slate-200">
                    <div>
                      <p className="font-medium text-slate-800">Faol holat</p>
                      <p className="text-xs text-slate-500">Siyosatni faollashtirish yoki vaqtincha to'xtatish</p>
                    </div>
                    <Toggle checked={form.is_active} onChange={() => setForm({ ...form, is_active: !form.is_active })} />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                      Settings (JSON) <span className="text-xs text-slate-400 font-normal">— ixtiyoriy</span>
                    </label>
                    <textarea
                      value={form.settings}
                      onChange={(e) => setForm({ ...form, settings: e.target.value })}
                      className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm font-mono focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow"
                      rows={6}
                      placeholder='{}'
                      spellCheck={false}
                    />
                    <p className="text-xs text-slate-400 mt-1">Qo'shimcha sozlamalar uchun JSON formatda ma'lumot kiriting</p>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 p-5 border-t border-slate-100 bg-slate-50/50">
              <button
                onClick={closeModal}
                className="px-4 py-2.5 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
                disabled={saving}
              >
                Bekor qilish
              </button>
              <button
                onClick={handleSave}
                className="px-5 py-2.5 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2 shadow-sm"
                disabled={saving}
              >
                {saving ? <Loader2 size={15} className="animate-spin" /> : <CheckCircle size={15} />}
                {saving ? "Saqlanmoqda..." : editing ? "Yangilash" : "Yaratish"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
