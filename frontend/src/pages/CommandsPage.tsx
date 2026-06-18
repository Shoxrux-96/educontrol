import { useState, useEffect } from "react";
import { RefreshCw, Send, XCircle, CheckCircle, Clock, AlertCircle } from "lucide-react";
import api from "../api/client";
import type { Command, Computer as ComputerType } from "../types";

export default function CommandsPage() {
  const [commands, setCommands] = useState<Command[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data: page } = await api.get<{ items: ComputerType[] }>("/computers?page_size=5");
        const computers = page.items || [];
        const all: Command[] = [];
        for (const c of computers) {
          try {
            const { data: cmds } = await api.get<Command[]>(`/computers/${c.id}/commands`);
            all.push(...cmds.map((cmd) => ({ ...cmd, computer_name: c.name })));
          } catch {}
        }
        setCommands(all.sort((a, b) => new Date(b.sent_at).getTime() - new Date(a.sent_at).getTime()));
      } catch {}
      setLoading(false);
    })();
  }, []);

  const statusIcon = (s: string) => {
    const m: Record<string, any> = { pending: Clock, sent: Send, delivered: RefreshCw, executed: CheckCircle, failed: XCircle };
    return m[s] || AlertCircle;
  };
  const statusColor = (s: string) => {
    const m: Record<string, string> = { pending: "text-amber-500", sent: "text-blue-500", delivered: "text-violet-500", executed: "text-emerald-500", failed: "text-rose-500" };
    return m[s] || "text-slate-500";
  };

  if (loading) return <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Buyruqlar</h1>
      </div>
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Tur</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Kompyuter</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Holat</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Yuborilgan</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Natija</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {commands.map((c) => {
              const Icon = statusIcon(c.status);
              return (
                <tr key={c.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-700">{c.command_type}</td>
                  <td className="px-4 py-3 text-slate-500">{c.computer_name || c.computer_id}</td>
                  <td className="px-4 py-3">
                    <span className={`flex items-center gap-1.5 ${statusColor(c.status)}`}>
                      <Icon size={14} /> {c.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500">{new Date(c.sent_at).toLocaleString("uz-UZ")}</td>
                  <td className="px-4 py-3 text-xs text-slate-400 max-w-[200px] truncate">
                    {c.result ? JSON.stringify(c.result) : "-"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {commands.length === 0 && <div className="text-center py-12 text-slate-400">Buyruqlar mavjud emas</div>}
      </div>
    </div>
  );
}
