import { Database, Shield, Bell, Mail } from "lucide-react";

const sections = [
  { icon: Database, title: "Ma'lumotlar bazasi", desc: "Database sozlamalari va zaxira nusxa" },
  { icon: Shield, title: "Xavfsizlik", desc: "JWT token, CORS va autentifikatsiya sozlamalari" },
  { icon: Bell, title: "Ogohlantirishlar", desc: "Email va boshqa bildirishnoma sozlamalari" },
  { icon: Mail, title: "SMTP", desc: "Email jo'natish sozlamalari" },
];

export default function SettingsPage() {
  return (
    <div>
      <h1 className="text-xl font-bold text-slate-800 mb-6">Tizim sozlamalari</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sections.map((s) => (
          <button key={s.title} className="bg-white rounded-xl border border-slate-200 p-5 text-left hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center mb-3">
              <s.icon size={20} className="text-slate-600" />
            </div>
            <h3 className="font-semibold text-slate-800">{s.title}</h3>
            <p className="text-sm text-slate-500 mt-1">{s.desc}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
