import { useState, useEffect } from "react";
import { Plus, Edit3, Trash2, Globe, X } from "lucide-react";
import api from "../api/client";

interface InternetRule {
  id: string;
  name: string;
  action: "allow" | "block" | "throttle" | "qos";
  target_type: "site" | "category" | "application";
  target_value: string;
  category?: string;
  bandwidth_limit?: number;
  is_active: boolean;
  priority: number;
  created_at: string;
}

interface RuleForm {
  name: string;
  action: string;
  target_type: string;
  target_value: string;
  category: string;
  bandwidth_limit: string;
  is_active: boolean;
  priority: string;
}

const emptyForm: RuleForm = {
  name: "", action: "allow", target_type: "site",
  target_value: "", category: "", bandwidth_limit: "",
  is_active: true, priority: "0",
};

export default function InternetRules() {
  const [rules, setRules] = useState<InternetRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<InternetRule | null>(null);
  const [form, setForm] = useState<RuleForm>(emptyForm);
  const [search, setSearch] = useState("");

  useEffect(() => { fetchRules(); }, []);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<InternetRule[]>("/internet/rules");
      setRules(data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const openAdd = () => {
    setEditing(null);
    setForm(emptyForm);
    setShowModal(true);
  };

  const openEdit = (rule: InternetRule) => {
    setEditing(rule);
    setForm({
      name: rule.name,
      action: rule.action,
      target_type: rule.target_type,
      target_value: rule.target_value,
      category: rule.category || "",
      bandwidth_limit: rule.bandwidth_limit?.toString() || "",
      is_active: rule.is_active,
      priority: rule.priority.toString(),
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    const payload = {
      name: form.name,
      action: form.action,
      target_type: form.target_type,
      target_value: form.target_value,
      category: form.category || undefined,
      bandwidth_limit: form.bandwidth_limit ? Number(form.bandwidth_limit) : undefined,
      is_active: form.is_active,
      priority: Number(form.priority),
    };
    try {
      if (editing) {
        await api.put(`/internet/rules/${editing.id}`, payload);
      } else {
        await api.post("/internet/rules", payload);
      }
      setShowModal(false);
      fetchRules();
    } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/internet/rules/${id}`);
      fetchRules();
    } catch { /* ignore */ }
  };

  const toggleStatus = async (rule: InternetRule) => {
    try {
      await api.patch(`/internet/rules/${rule.id}`, { is_active: !rule.is_active });
      setRules((prev) => prev.map((r) => r.id === rule.id ? { ...r, is_active: !r.is_active } : r));
    } catch { /* ignore */ }
  };

  const actionBadge = (a: string) => {
    const m: Record<string, string> = {
      allow: "bg-emerald-100 text-emerald-700",
      block: "bg-rose-100 text-rose-700",
      throttle: "bg-amber-100 text-amber-700",
      qos: "bg-blue-100 text-blue-700",
    };
    return m[a] || "bg-slate-100 text-slate-600";
  };

  const filtered = rules.filter((r) =>
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    r.target_value.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Internet qoidalari</h1>
        <div className="flex items-center gap-3">
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            className="pl-3 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Qidirish..." />
          <button onClick={openAdd} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
            <Plus size={16} /> Yangi qoida
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                  <th className="text-left px-4 py-3 font-medium">Nomi</th>
                  <th className="text-left px-4 py-3 font-medium">Amal</th>
                  <th className="text-left px-4 py-3 font-medium">Maqsad turi</th>
                  <th className="text-left px-4 py-3 font-medium">Maqsad qiymati</th>
                  <th className="text-left px-4 py-3 font-medium">Kategoriya</th>
                  <th className="text-left px-4 py-3 font-medium">Cheklov</th>
                  <th className="text-center px-4 py-3 font-medium">Holat</th>
                  <th className="text-center px-4 py-3 font-medium">Prioritet</th>
                  <th className="text-right px-4 py-3 font-medium">Amallar</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-800">{r.name}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${actionBadge(r.action)}`}>{r.action}</span>
                    </td>
                    <td className="px-4 py-3 text-slate-600 capitalize">{r.target_type}</td>
                    <td className="px-4 py-3 text-slate-600">{r.target_value}</td>
                    <td className="px-4 py-3 text-slate-600">{r.category || "—"}</td>
                    <td className="px-4 py-3 text-slate-600">{r.bandwidth_limit ? `${r.bandwidth_limit} Mbps` : "—"}</td>
                    <td className="px-4 py-3 text-center">
                      <button onClick={() => toggleStatus(r)}
                        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${r.is_active ? "bg-emerald-500" : "bg-slate-300"}`}>
                        <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${r.is_active ? "translate-x-4.5" : "translate-x-1"}`} />
                      </button>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="text-xs font-mono bg-slate-100 px-2 py-1 rounded">{r.priority}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button onClick={() => openEdit(r)} className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg">
                        <Edit3 size={14} />
                      </button>
                      <button onClick={() => handleDelete(r.id)} className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg ml-1">
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filtered.length === 0 && <div className="text-center py-12 text-slate-400">Qoidalar mavjud emas</div>}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">{editing ? "Qoidani tahrirlash" : "Yangi qoida"}</h2>
              <button onClick={() => setShowModal(false)} className="p-1 text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Nomi</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Amal</label>
                  <select value={form.action} onChange={(e) => setForm({ ...form, action: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="allow">Allow</option>
                    <option value="block">Block</option>
                    <option value="throttle">Throttle</option>
                    <option value="qos">QoS</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Maqsad turi</label>
                  <select value={form.target_type} onChange={(e) => setForm({ ...form, target_type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="site">Site</option>
                    <option value="category">Category</option>
                    <option value="application">Application</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Maqsad qiymati</label>
                <input type="text" value={form.target_value} onChange={(e) => setForm({ ...form, target_value: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Kategoriya</label>
                  <input type="text" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Bandwidth limit (Mbps)</label>
                  <input type="number" value={form.bandwidth_limit} onChange={(e) => setForm({ ...form, bandwidth_limit: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Prioritet</label>
                  <input type="number" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div className="flex items-end pb-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                      className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                    <span className="text-sm text-slate-600">Faol</span>
                  </label>
                </div>
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
