import { useState, useEffect } from "react";
import { ShieldCheck, Plus, ToggleLeft, ToggleRight } from "lucide-react";
import api from "../api/client";
import type { Policy } from "../types";

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);

  useEffect(() => {
    api.get<Policy[]>("/policies").then((r) => setPolicies(r.data)).catch(() => {});
  }, []);

  const togglePolicy = async (id: string, active: boolean) => {
    await api.patch(`/policies/${id}`, { is_active: active });
    setPolicies((prev) => prev.map((p) => (p.id === id ? { ...p, is_active: active } : p)));
  };

  const typeIcon: Record<string, string> = { internet: "🌐", application: "📱", usb: "💾", print_screen: "📸" };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Siyosatlar</h1>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
          <Plus size={16} /> Yangi siyosat
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {policies.map((p) => (
          <div key={p.id} className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-violet-50 rounded-xl flex items-center justify-center text-lg">
                  {typeIcon[p.policy_type] || <ShieldCheck size={20} className="text-violet-600" />}
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800">{p.name}</h3>
                  <p className="text-xs text-slate-400 capitalize">{p.policy_type}</p>
                </div>
              </div>
              <button onClick={() => togglePolicy(p.id, !p.is_active)} className={p.is_active ? "text-emerald-500" : "text-slate-300"}>
                {p.is_active ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
              </button>
            </div>
            {p.description && <p className="text-sm text-slate-500 mt-2">{p.description}</p>}
            <pre className="mt-3 bg-slate-50 rounded-lg p-3 text-xs text-slate-600 overflow-x-auto">
              {JSON.stringify(p.config, null, 2)}
            </pre>
          </div>
        ))}
        {policies.length === 0 && (
          <div className="col-span-full text-center py-12 text-slate-400">Hali siyosatlar mavjud emas</div>
        )}
      </div>
    </div>
  );
}
