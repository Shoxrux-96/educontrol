import { useState, useEffect } from "react";
import { LayoutDashboard, Computer, ShieldCheck, AlertTriangle, Terminal } from "lucide-react";
import api from "../api/client";
import type { DashboardStats } from "../types";
import { StatCard } from "../components/Layout";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    api.get<DashboardStats>("/monitoring/dashboard").then((r) => setStats(r.data)).catch(() => {});
  }, []);

  const cards = [
    { title: "Jami kompyuterlar", value: stats?.total_computers ?? 0, icon: Computer, color: "indigo" },
    { title: "Online", value: stats?.online_computers ?? 0, icon: LayoutDashboard, color: "emerald" },
    { title: "Offline", value: stats?.offline_computers ?? 0, icon: LayoutDashboard, color: "rose" },
    { title: "Faol siyosatlar", value: stats?.active_policies ?? 0, icon: ShieldCheck, color: "blue" },
    { title: "Bugungi ogohlantirishlar", value: stats?.alerts_today ?? 0, icon: AlertTriangle, color: "amber" },
    { title: "Bugungi buyruqlar", value: stats?.commands_today ?? 0, icon: Terminal, color: "violet" },
  ];

  return (
    <div>
      <h1 className="text-xl font-bold text-slate-800 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {cards.map((c) => <StatCard key={c.title} {...c} />)}
      </div>
    </div>
  );
}
