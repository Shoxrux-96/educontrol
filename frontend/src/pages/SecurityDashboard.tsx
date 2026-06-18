import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, ShieldAlert, ShieldCheck, ShieldOff, Usb, Bug, UserX, LogIn, AlertTriangle, RefreshCw, XCircle, ArrowRight, Eye } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface SecuritySummary {
  total_usb_events: number;
  blocked_usb: number;
  total_threats: number;
  critical_threats: number;
  unresolved_threats: number;
  no_av: number;
  outdated_av: number;
  failed_logins: number;
}

interface Threat {
  id: string;
  threat_type: string;
  severity: string;
  computer_name: string;
  created_at: string;
}

interface LoginEvent {
  id: string;
  computer_name: string;
  username: string;
  result: string;
  created_at: string;
}

const quickLinks = [
  { title: "USB Qurilmalar", desc: "USB qurilmalar monitoringi va boshqaruvi", icon: Usb, href: "/security/usb" },
  { title: "Antivirus Monitoring", desc: "Antivirus holati va yangilanishlar", icon: ShieldCheck, href: "/security/antivirus" },
  { title: "Login Auditi", desc: "Tizimga kirish urinishlari kuzatuvi", icon: LogIn, href: "/security/logins" },
  { title: "Xavfsizlik sozlamalari", desc: "Xavfsizlik siyosatlari va sozlamalar", icon: Shield, href: "/security/policies" },
];

const severityColor: Record<string, string> = {
  critical: "text-rose-600 bg-rose-50",
  high: "text-amber-600 bg-amber-50",
  medium: "text-yellow-600 bg-yellow-50",
  low: "text-slate-600 bg-slate-100",
};

export default function SecurityDashboard() {
  const [summary, setSummary] = useState<SecuritySummary | null>(null);
  const [threats, setThreats] = useState<Threat[]>([]);
  const [logins, setLogins] = useState<LoginEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAdmin } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.get<SecuritySummary>("/security/summary"),
      api.get<{ items: Threat[] }>("/security/threats?limit=10"),
      api.get<{ items: LoginEvent[] }>("/security/logins?result=failed&limit=10"),
    ])
      .then(([s, t, l]) => {
        setSummary(s.data);
        setThreats(t.data.items || []);
        setLogins(l.data.items || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const cards = summary
    ? [
        { label: "Umumiy USB hodisalar", value: summary.total_usb_events, icon: Usb, color: "bg-indigo-50 text-indigo-600" },
        { label: "Bloklangan USB", value: summary.blocked_usb, icon: XCircle, color: "bg-rose-50 text-rose-600" },
        { label: "Jami tahdidlar", value: summary.total_threats, icon: Bug, color: "bg-amber-50 text-amber-600" },
        { label: "Kritik tahdidlar", value: summary.critical_threats, icon: AlertTriangle, color: "bg-rose-50 text-rose-600" },
        { label: "Hal qilinmagan tahdidlar", value: summary.unresolved_threats, icon: ShieldOff, color: "bg-violet-50 text-violet-600" },
        { label: "AV o'rnatilmagan", value: summary.no_av, icon: Shield, color: "bg-slate-100 text-slate-600" },
        { label: "AV eskirgan", value: summary.outdated_av, icon: RefreshCw, color: "bg-amber-50 text-amber-600" },
        { label: "Muvaffaqiyatsiz kirishlar", value: summary.failed_logins, icon: UserX, color: "bg-rose-50 text-rose-600" },
      ]
    : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Kiberxavfsizlik Dashbordi</h1>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {cards.map((c) => (
          <div key={c.label} className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${c.color}`}>
              <c.icon size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">{c.value}</p>
              <p className="text-xs text-slate-500">{c.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {quickLinks.map((link) => (
          <button
            key={link.title}
            onClick={() => navigate(link.href)}
            className="bg-white rounded-xl border border-slate-200 p-5 text-left hover:shadow-md hover:border-indigo-200 transition-all group"
          >
            <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center mb-3 group-hover:bg-indigo-100 transition-colors">
              <link.icon size={20} className="text-indigo-600" />
            </div>
            <h3 className="font-semibold text-slate-800 mb-1">{link.title}</h3>
            <p className="text-xs text-slate-400">{link.desc}</p>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-800 flex items-center gap-2">
              <Bug size={18} className="text-amber-500" /> So'nggi tahdidlar
            </h2>
            {isAdmin && (
              <button onClick={() => navigate("/security/threats")} className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
                Barchasi <ArrowRight size={14} />
              </button>
            )}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-400 text-xs">
                  <th className="pb-2 font-medium">Tahdid turi</th>
                  <th className="pb-2 font-medium">Daraja</th>
                  <th className="pb-2 font-medium">Kompyuter</th>
                  <th className="pb-2 font-medium">Sana</th>
                  <th className="pb-2 font-medium" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {threats.map((t) => (
                  <tr key={t.id} className="text-slate-600">
                    <td className="py-2.5">{t.threat_type}</td>
                    <td className="py-2.5">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${severityColor[t.severity] || severityColor.low}`}>
                        {t.severity}
                      </span>
                    </td>
                    <td className="py-2.5">{t.computer_name}</td>
                    <td className="py-2.5 text-slate-400">{new Date(t.created_at).toLocaleString("uz-UZ")}</td>
                    <td className="py-2.5">
                      <button onClick={() => navigate(`/security/threats/${t.id}`)} className="text-slate-400 hover:text-indigo-600">
                        <Eye size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
                {threats.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-400">Tahdidlar mavjud emas</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-800 flex items-center gap-2">
              <UserX size={18} className="text-rose-500" /> Muvaffaqiyatsiz kirishlar
            </h2>
            {isAdmin && (
              <button onClick={() => navigate("/security/logins")} className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
                Barchasi <ArrowRight size={14} />
              </button>
            )}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-400 text-xs">
                  <th className="pb-2 font-medium">Foydalanuvchi</th>
                  <th className="pb-2 font-medium">Kompyuter</th>
                  <th className="pb-2 font-medium">Natija</th>
                  <th className="pb-2 font-medium">Sana</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logins.map((l) => (
                  <tr key={l.id} className="text-slate-600">
                    <td className="py-2.5">{l.username}</td>
                    <td className="py-2.5">{l.computer_name}</td>
                    <td className="py-2.5">
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-rose-50 text-rose-600">
                        {l.result}
                      </span>
                    </td>
                    <td className="py-2.5 text-slate-400">{new Date(l.created_at).toLocaleString("uz-UZ")}</td>
                  </tr>
                ))}
                {logins.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-slate-400">Muvaffaqiyatsiz kirishlar mavjud emas</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
