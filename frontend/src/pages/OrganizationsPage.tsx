import { useState, useEffect } from "react";
import { Building2, Plus, Monitor, Users, ShieldCheck, Search } from "lucide-react";
import api from "../api/client";
import type { Organization } from "../types";

export default function OrganizationsPage() {
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.get<Organization[]>("/organizations").then((r) => setOrgs(r.data)).catch(() => {});
  }, []);

  const filtered = orgs.filter((o) =>
    o.name.toLowerCase().includes(search.toLowerCase()) ||
    o.slug.includes(search)
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Tashkilotlar</h1>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
          <Plus size={16} /> Yangi tashkilot
        </button>
      </div>

      <div className="relative mb-6">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text" value={search} onChange={(e) => setSearch(e.target.value)}
          className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm w-full max-w-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder="Tashkilot qidirish..."
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((org) => (
          <div key={org.id} className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center">
                <Building2 size={20} className="text-indigo-600" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-800">{org.name}</h3>
                <p className="text-xs text-slate-400">{org.slug}</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3 text-center mb-4">
              <div className="bg-slate-50 rounded-lg p-2">
                <Users size={16} className="mx-auto text-slate-500 mb-1" />
                <p className="text-sm font-semibold text-slate-700">{org.user_count ?? 0}</p>
                <p className="text-xs text-slate-400">Foydalanuvchi</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-2">
                <Monitor size={16} className="mx-auto text-slate-500 mb-1" />
                <p className="text-sm font-semibold text-slate-700">{org.computer_count ?? 0}</p>
                <p className="text-xs text-slate-400">Kompyuter</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-2">
                <ShieldCheck size={16} className="mx-auto text-slate-500 mb-1" />
                <p className="text-sm font-semibold text-slate-700">{org.policy_count ?? 0}</p>
                <p className="text-xs text-slate-400">Siyosat</p>
              </div>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className={`px-2 py-0.5 rounded-full ${org.is_active ? "bg-emerald-50 text-emerald-600" : "bg-slate-100 text-slate-400"}`}>
                {org.is_active ? "Faol" : "Faol emas"}
              </span>
              <span className="text-slate-400">Max: {org.max_computers} kompyuter</span>
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="col-span-full text-center py-12 text-slate-400">Tashkilot topilmadi</div>
        )}
      </div>
    </div>
  );
}
