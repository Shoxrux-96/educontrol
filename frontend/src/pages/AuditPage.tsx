import { useState, useEffect } from "react";
import { Info, AlertTriangle, AlertCircle } from "lucide-react";
import api from "../api/client";
import type { AuditLog } from "../types";

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);

  useEffect(() => {
    api.get<{ items: AuditLog[] }>("/audit").then((r) => setLogs(r.data.items || [])).catch(() => {});
  }, []);

  const sevIcon = (s: string) => {
    const m: Record<string, any> = { info: Info, warning: AlertTriangle, critical: AlertCircle };
    return m[s] || Info;
  };
  const sevColor = (s: string) => {
    const m: Record<string, string> = { info: "text-blue-600 bg-blue-50", warning: "text-amber-600 bg-amber-50", critical: "text-rose-600 bg-rose-50" };
    return m[s] || "text-slate-600 bg-slate-50";
  };

  return (
    <div>
      <h1 className="text-xl font-bold text-slate-800 mb-6">Audit jurnali</h1>
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Daraja</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Turi</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Tavsif</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Vaqt</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {logs.map((l) => {
              const Icon = sevIcon(l.severity);
              return (
                <tr key={l.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${sevColor(l.severity)}`}>
                      <Icon size={12} /> {l.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{l.event_type}</td>
                  <td className="px-4 py-3 text-slate-500 max-w-xs truncate">{l.description}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{new Date(l.created_at).toLocaleString("uz-UZ")}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {logs.length === 0 && <div className="text-center py-12 text-slate-400">Audit yozuvlari mavjud emas</div>}
      </div>
    </div>
  );
}
