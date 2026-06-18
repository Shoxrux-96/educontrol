import { useState, useEffect } from "react";
import { Users, Plus, Monitor, Pencil, Trash2, X, Loader2, AlertTriangle } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";
import type { ComputerGroup } from "../types";

const COLORS = [
  { value: "blue", label: "Ko‘k", class: "border-blue-400 bg-blue-50 ring-blue-400" },
  { value: "emerald", label: "Yashil", class: "border-emerald-400 bg-emerald-50 ring-emerald-400" },
  { value: "amber", label: "Sariq", class: "border-amber-400 bg-amber-50 ring-amber-400" },
  { value: "violet", label: "Binafsha", class: "border-violet-400 bg-violet-50 ring-violet-400" },
  { value: "rose", label: "Pushti", class: "border-rose-400 bg-rose-50 ring-rose-400" },
  { value: "cyan", label: "Havo rang", class: "border-cyan-400 bg-cyan-50 ring-cyan-400" },
];

const colorMap: Record<string, string> = Object.fromEntries(
  COLORS.map((c) => [c.value, c.class])
);

const defaultForm = { name: "", description: "", color: "blue" };

export default function GroupsPage() {
  const { user } = useAuth();
  const canModify = user?.role === "owner" || user?.role === "admin";
  const [groups, setGroups] = useState<ComputerGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<ComputerGroup | null>(null);
  const [form, setForm] = useState(defaultForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchGroups = () => {
    setLoading(true);
    api.get<ComputerGroup[]>("/computers/groups")
      .then((r) => setGroups(Array.isArray(r.data) ? r.data : []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchGroups(); }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(defaultForm);
    setError("");
    setModalOpen(true);
  };

  const openEdit = (g: ComputerGroup) => {
    setEditing(g);
    setForm({ name: g.name, description: g.description || "", color: g.color || "blue" });
    setError("");
    setModalOpen(true);
  };

  const closeModal = () => {
    if (saving) return;
    setModalOpen(false);
    setEditing(null);
    setForm(defaultForm);
    setError("");
  };

  const validate = () => {
    if (!form.name.trim()) {
      setError("Guruh nomini kiriting");
      return false;
    }
    return true;
  };

  const handleSave = async () => {
    if (!validate()) return;
    setSaving(true);
    setError("");
    try {
      if (editing) {
        await api.patch(`/computers/groups/${editing.id}`, form);
      } else {
        await api.post("/computers/groups", form);
      }
      closeModal();
      fetchGroups();
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Saqlashda xatolik yuz berdi");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    setDeleting(true);
    try {
      await api.delete(`/computers/groups/${id}`);
      setDeleteConfirm(null);
      fetchGroups();
    } catch {
      setError("O‘chirishda xatolik yuz berdi");
    } finally {
      setDeleting(false);
    }
  };

  const confirmDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setDeleteConfirm(id);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Guruhlar</h1>
          <p className="text-sm text-slate-500 mt-0.5">{groups.length} ta guruh</p>
        </div>
        {canModify && (
          <button
            onClick={openCreate}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm"
          >
            <Plus size={16} /> Yangi guruh
          </button>
        )}
      </div>

      {error && !modalOpen && (
        <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-sm text-rose-700 flex items-center gap-2">
          <AlertTriangle size={16} /> {error}
          <button onClick={() => setError("")} className="ml-auto text-rose-400 hover:text-rose-600"><X size={14} /></button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 size={24} className="text-indigo-500 animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {groups.map((g) => (
            <div
              key={g.id}
              className={`rounded-xl border-2 p-5 relative group transition-shadow hover:shadow-md ${colorMap[g.color || ""] || "border-slate-200 bg-white"}`}
            >
              {canModify && (
                <div className="absolute top-3 right-3 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => openEdit(g)}
                    className="p-1.5 rounded-lg bg-white/80 text-slate-500 hover:text-indigo-600 hover:bg-white transition-colors"
                    title="Tahrirlash"
                  >
                    <Pencil size={14} />
                  </button>
                  <button
                    onClick={(e) => confirmDelete(e, g.id)}
                    className="p-1.5 rounded-lg bg-white/80 text-slate-500 hover:text-rose-600 hover:bg-white transition-colors"
                    title="O‘chirish"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              )}

              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm">
                  <Users size={20} className="text-slate-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-slate-800 truncate">{g.name}</h3>
                  {g.description && <p className="text-xs text-slate-500 truncate">{g.description}</p>}
                </div>
              </div>

              <div className="flex items-center gap-1.5 text-sm text-slate-600">
                <Monitor size={14} className="text-slate-400" />
                <span>{g.computer_count ?? 0} kompyuter</span>
              </div>

              {deleteConfirm === g.id && (
                <div className="absolute inset-0 rounded-xl bg-white/95 backdrop-blur-sm flex items-center justify-center z-10">
                  <div className="text-center p-4">
                    <p className="text-sm font-medium text-slate-700 mb-3">Guruhni o‘chirishni tasdiqlaysizmi?</p>
                    <div className="flex gap-2 justify-center">
                      <button
                        onClick={() => setDeleteConfirm(null)}
                        className="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors"
                        disabled={deleting}
                      >
                        Bekor qilish
                      </button>
                      <button
                        onClick={() => handleDelete(g.id)}
                        className="px-3 py-1.5 text-xs font-medium rounded-lg bg-rose-600 text-white hover:bg-rose-700 transition-colors flex items-center gap-1"
                        disabled={deleting}
                      >
                        {deleting ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
                        O‘chirish
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
          {groups.length === 0 && (
            <div className="col-span-full text-center py-16">
              <Users size={40} className="mx-auto text-slate-300 mb-3" />
              <p className="text-slate-400 mb-4">Hali guruhlar yaratilmagan</p>
              <button
                onClick={openCreate}
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                <Plus size={16} /> Birinchi guruhni yaratish
              </button>
            </div>
          )}
        </div>
      )}

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={closeModal}>
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-5 border-b border-slate-100">
              <div>
                <h2 className="text-lg font-bold text-slate-800">
                  {editing ? "Guruhni tahrirlash" : "Yangi guruh"}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  {editing ? "Guruh ma'lumotlarini yangilang" : "Kompyuterlar guruhini yarating"}
                </p>
              </div>
              <button
                onClick={closeModal}
                className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <div className="p-5 space-y-4">
              {error && (
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-sm text-rose-700 flex items-center gap-2">
                  <AlertTriangle size={15} /> {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Guruh nomi <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => { setForm({ ...form, name: e.target.value }); setError(""); }}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow"
                  placeholder="Masalan: 1-qavat, Matematika xonasi"
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
                  placeholder="Guruh haqida qisqacha ma'lumot"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Rang</label>
                <div className="flex gap-2.5 flex-wrap">
                  {COLORS.map((c) => (
                    <button
                      key={c.value}
                      onClick={() => setForm({ ...form, color: c.value })}
                      className={`w-9 h-9 rounded-xl border-2 transition-all ${
                        form.color === c.value
                          ? `${c.class} ring-2 ring-offset-2 scale-110`
                          : "border-slate-200 bg-white hover:border-slate-300"
                      }`}
                      title={c.label}
                    />
                  ))}
                </div>
                <p className="text-xs text-slate-400 mt-1.5">
                  Tanlangan: <span className="font-medium text-slate-600">{COLORS.find((c) => c.value === form.color)?.label}</span>
                </p>
              </div>
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
                {saving ? <Loader2 size={15} className="animate-spin" /> : <Plus size={15} />}
                {saving ? "Saqlanmoqda..." : editing ? "Yangilash" : "Yaratish"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
