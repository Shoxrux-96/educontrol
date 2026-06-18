import { useState, useEffect } from "react";
import { CheckCircle, AlertTriangle, Activity } from "lucide-react";
import api from "../api/client";
import type { AlertEvent, AlertRule } from "../types";

export default function MonitoringPage() {
  const [events, setEvents] = useState<AlertEvent[]>([]);
  const [rules, setRules] = useState<AlertRule[]>([]);

  useEffect(() => {
    api.get<AlertEvent[]>("/monitoring/alerts").then((r) => setEvents(r.data)).catch(() => {});
    api.get<AlertRule[]>("/monitoring/alerts/rules").then((r) => setRules(r.data)).catch(() => {});
  }, []);

  const acknowledge = async (id: string) => {
    await api.post(`/monitoring/alerts/${id}/acknowledge`);
    setEvents((prev) => prev.map((e) => (e.id === id ? { ...e, acknowledged: true } : e)));
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <h1 className="text-xl font-bold text-slate-800 mb-4">Ogohlantirishlar</h1>
        <div className="space-y-3">
          {events.map((e) => (
            <div key={e.id} className={`bg-white rounded-xl border p-4 ${e.acknowledged ? "border-slate-200" : "border-amber-300 bg-amber-50/50"}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <AlertTriangle size={20} className={e.acknowledged ? "text-slate-400" : "text-amber-500"} />
                  <div>
                    <h3 className="font-semibold text-sm">{e.rule_name}</h3>
                    <p className="text-xs text-slate-500">
                      {e.metric}: {e.actual_value} (chegara: {e.threshold})
                    </p>
                  </div>
                </div>
                {!e.acknowledged && (
                  <button onClick={() => acknowledge(e.id)} className="flex items-center gap-1 text-xs text-emerald-600 hover:bg-emerald-50 px-2 py-1 rounded">
                    <CheckCircle size={14} /> Tasdiqlash
                  </button>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-2">{new Date(e.triggered_at).toLocaleString("uz-UZ")}</p>
            </div>
          ))}
          {events.length === 0 && <div className="text-center py-12 text-slate-400">Ogohlantirishlar mavjud emas</div>}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Qoidalar</h2>
        <div className="space-y-3">
          {rules.map((r) => (
            <div key={r.id} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-center gap-2 mb-2">
                <Activity size={16} className="text-indigo-500" />
                <h3 className="font-medium text-sm">{r.name}</h3>
              </div>
              <p className="text-xs text-slate-500">
                {r.metric} {r.condition} {r.threshold}
              </p>
              <div className="flex items-center gap-2 mt-2">
                <span className={`w-2 h-2 rounded-full ${r.enabled ? "bg-emerald-500" : "bg-slate-300"}`} />
                <span className="text-xs text-slate-400">{r.enabled ? "Faol" : "Faol emas"}</span>
              </div>
            </div>
          ))}
          {rules.length === 0 && <div className="text-center py-8 text-slate-400">Qoidalar mavjud emas</div>}
        </div>
      </div>
    </div>
  );
}
