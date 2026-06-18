import { useState, useEffect } from "react";
import { Plus, MessageSquare, ChevronDown, ChevronRight, X } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface TicketComment {
  id: string;
  author: string;
  body: string;
  created_at: string;
}

interface Ticket {
  id: string;
  title: string;
  category: "hardware" | "software" | "network" | "other";
  priority: "low" | "medium" | "high" | "critical";
  status: "open" | "in_progress" | "resolved" | "closed";
  created_by: string;
  assigned_to?: string;
  description?: string;
  comments?: TicketComment[];
  created_at: string;
  updated_at: string;
}

interface TicketForm {
  title: string;
  category: string;
  priority: string;
  description: string;
}

const emptyForm: TicketForm = { title: "", category: "software", priority: "medium", description: "" };

const statusBadge: Record<string, string> = {
  open: "bg-amber-100 text-amber-700",
  in_progress: "bg-blue-100 text-blue-700",
  resolved: "bg-emerald-100 text-emerald-700",
  closed: "bg-slate-100 text-slate-500",
};

const priorityBadge: Record<string, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-amber-100 text-amber-700",
  critical: "bg-rose-100 text-rose-700",
};

export default function HelpDeskTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<TicketForm>(emptyForm);
  const { user } = useAuth();

  useEffect(() => { fetchTickets(); }, []);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<Ticket[]>("/helpdesk/tickets");
      setTickets(data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const toggleExpand = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleCreate = async () => {
    try {
      await api.post("/helpdesk/tickets", form);
      setShowModal(false);
      setForm(emptyForm);
      fetchTickets();
    } catch { /* ignore */ }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Helpdesk chiptalar</h1>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
          <Plus size={16} /> Yangi chipta
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>
      ) : (
        <div className="space-y-3">
          {tickets.map((t) => (
            <div key={t.id} className="bg-white rounded-xl border border-slate-200">
              <div className="p-5 cursor-pointer" onClick={() => toggleExpand(t.id)}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    {expanded.has(t.id) ? <ChevronDown size={16} className="text-slate-400 shrink-0" /> : <ChevronRight size={16} className="text-slate-400 shrink-0" />}
                    <div className="min-w-0">
                      <h3 className="font-semibold text-slate-800 truncate">{t.title}</h3>
                      <p className="text-xs text-slate-400 mt-0.5">{t.category} • {t.created_by}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 ml-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${priorityBadge[t.priority]}`}>{t.priority}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge[t.status]}`}>{t.status.replace("_", " ")}</span>
                    <span className="text-xs text-slate-400 whitespace-nowrap">{new Date(t.created_at).toLocaleDateString("uz-UZ")}</span>
                  </div>
                </div>
              </div>
              {expanded.has(t.id) && (
                <div className="px-5 pb-5 pt-0 border-t border-slate-100">
                  {t.description && <p className="text-sm text-slate-600 mt-3">{t.description}</p>}
                  {t.assigned_to && <p className="text-xs text-slate-400 mt-2">Tayinlangan: {t.assigned_to}</p>}
                  <div className="mt-4 space-y-3">
                    <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Izohlar</h4>
                    {t.comments && t.comments.length > 0 ? t.comments.map((c) => (
                      <div key={c.id} className="bg-slate-50 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-slate-700">{c.author}</span>
                          <span className="text-xs text-slate-400">{new Date(c.created_at).toLocaleString("uz-UZ")}</span>
                        </div>
                        <p className="text-sm text-slate-600">{c.body}</p>
                      </div>
                    )) : (
                      <p className="text-sm text-slate-400 italic">Izohlar mavjud emas</p>
                    )}
                  </div>
                  <div className="mt-3 flex items-center gap-2 text-xs text-slate-400">
                    <MessageSquare size={12} />
                    <span>{(t.comments?.length || 0)} ta izoh</span>
                    <span className="text-slate-200">|</span>
                    <span>Oxirgi yangilanish: {new Date(t.updated_at).toLocaleString("uz-UZ")}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
          {tickets.length === 0 && <div className="text-center py-12 text-slate-400">Chiptalar mavjud emas</div>}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">Yangi chipta</h2>
              <button onClick={() => setShowModal(false)} className="p-1 text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Sarlavha</label>
                <input type="text" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Kategoriya</label>
                  <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="hardware">Hardware</option>
                    <option value="software">Software</option>
                    <option value="network">Network</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Prioritet</label>
                  <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Tavsif</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={4}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
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
