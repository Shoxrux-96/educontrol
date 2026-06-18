import { useState, useEffect, useMemo } from "react";
import { Outlet, NavLink, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../api/AuthContext";
import {
  Monitor, LayoutDashboard, Computer,
  History, Bell, BarChart3, LogOut, Menu, X,
  Users, MessageSquare, Building2, Settings, Globe,
  Activity, Headphones, Network, Server,
  Building, FileJson, Package, Shield, HardDrive, LogIn,
  BookOpen, Bot, Save, ChevronDown, ChevronRight,
} from "lucide-react";

const ALL_GROUPS = [
  {
    label: "Asosiy",
    icon: LayoutDashboard,
    items: [
      { to: "/dashboard", label: "Dashboard" },
      { to: "/monitoring", label: "Monitoring" },
      { to: "/reports", label: "Hisobotlar" },
      { to: "/audit", label: "Audit" },
    ],
  },
  {
    label: "Qurilmalar",
    icon: Computer,
    items: [
      { to: "/computers", label: "Kompyuterlar" },
      { to: "/groups", label: "Guruhlar" },
      { to: "/policies", label: "Siyosatlar" },
      { to: "/commands", label: "Buyruqlar" },
      { to: "/messages", label: "Xabarlar" },
      { to: "/software", label: "Dasturlar" },
    ],
  },
  {
    label: "Tarmoq",
    icon: Network,
    items: [
      { to: "/network/topology", label: "Tarmoq xaritasi" },
      { to: "/network/ip", label: "IP boshqaruvi" },
      { to: "/network/ping", label: "Ping monitoring" },
      { to: "/network/bandwidth", label: "Bandwidth" },
      { to: "/enterprise/syslog", label: "Syslog" },
      { to: "/enterprise/snmp", label: "SNMP" },
    ],
  },
  {
    label: "Internet",
    icon: Globe,
    items: [
      { to: "/internet", label: "Internet qoidalari" },
      { to: "/firewall", label: "Firewall" },
      { to: "/traffic", label: "Trafik" },
      { to: "/vpn", label: "VPN" },
    ],
  },
  {
    label: "Xavfsizlik",
    icon: Shield,
    items: [
      { to: "/security", label: "Xavfsizlik paneli" },
      { to: "/security/usb", label: "USB nazorat" },
      { to: "/security/antivirus", label: "Antivirus" },
      { to: "/security/logins", label: "Login audit" },
      { to: "/ad", label: "Active Directory" },
      { to: "/ad/gpo", label: "Group Policy" },
    ],
  },
  {
    label: "Xizmatlar",
    icon: Headphones,
    items: [
      { to: "/helpdesk", label: "Help Desk" },
      { to: "/ai", label: "AI Administrator" },
      { to: "/enterprise/backup", label: "Backup" },
    ],
  },
  {
    label: "Ta'lim",
    icon: BookOpen,
    items: [
      { to: "/education/exams", label: "Imtihonlar" },
    ],
  },
  {
    label: "Tizim",
    icon: Settings,
    items: [
      { to: "/organizations", label: "Tashkilotlar" },
      { to: "/settings", label: "Sozlamalar" },
    ],
  },
];

const ADMIN_ONLY = new Set([
  "/monitoring", "/groups", "/policies", "/commands", "/messages", "/software",
  "/internet", "/firewall", "/vpn", "/network/topology", "/network/ip",
  "/network/ping", "/network/bandwidth", "/ad", "/ad/gpo",
  "/security", "/security/usb", "/security/antivirus",
  "/ai", "/enterprise/syslog", "/enterprise/snmp", "/enterprise/backup",
  "/education/exams",
]);

const OWNER_ONLY = new Set(["/organizations", "/settings"]);

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout, isOwner, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const groups = useMemo(() => {
    return ALL_GROUPS
      .map((g) => ({
        ...g,
        items: g.items.filter((i) => {
          if (OWNER_ONLY.has(i.to)) return isOwner;
          if (ADMIN_ONLY.has(i.to)) return isAdmin;
          return true;
        }),
      }))
      .filter((g) => g.items.length > 0);
  }, [isOwner, isAdmin]);

  const initialExpanded = useMemo(() => {
    const active = groups.find((g) =>
      g.items.some((i) => i.to === location.pathname || (i.to !== "/" && location.pathname.startsWith(i.to)))
    );
    return new Set(active ? [active.label] : []);
  }, []);

  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(initialExpanded);

  useEffect(() => {
    const active = groups.find((g) =>
      g.items.some((i) => i.to === location.pathname || (i.to !== "/" && location.pathname.startsWith(i.to)))
    );
    if (active) {
      setExpandedGroups((prev) => {
        if (prev.has(active.label)) return prev;
        return new Set([...prev, active.label]);
      });
    }
  }, [location.pathname, groups]);

  const toggleGroup = (label: string) => {
    setExpandedGroups((prev) => {
      const next = new Set(prev);
      if (next.has(label)) next.delete(label);
      else next.add(label);
      return next;
    });
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <aside className={`fixed inset-y-0 left-0 z-30 w-64 bg-slate-900 text-white transform transition-transform lg:translate-x-0 lg:static lg:inset-auto ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex items-center gap-3 px-6 h-16 border-b border-slate-700">
          <Monitor className="w-6 h-6 text-indigo-400" />
          <span className="font-bold text-lg">EDU Control</span>
        </div>
        <nav className="p-3 space-y-1 overflow-y-auto" style={{ height: "calc(100vh - 4rem)" }}>
          {groups.map((group) => {
            const isExpanded = expandedGroups.has(group.label);
            const GroupIcon = group.icon;
            return (
              <div key={group.label}>
                <button
                  onClick={() => toggleGroup(group.label)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-colors ${isExpanded ? "text-indigo-300" : "text-slate-500 hover:text-slate-300"}`}
                >
                  <GroupIcon size={14} />
                  <span className="flex-1 text-left">{group.label}</span>
                  {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </button>
                {isExpanded && (
                  <div className="ml-1 mt-1 space-y-0.5 border-l border-slate-700 pl-2">
                    {group.items.map((item) => (
                      <NavLink
                        key={item.to}
                        to={item.to}
                        end={item.to === "/dashboard"}
                        onClick={() => setSidebarOpen(false)}
                        className={({ isActive }) =>
                          `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                            isActive
                              ? "bg-indigo-600/20 text-indigo-300 font-medium"
                              : "text-slate-300 hover:bg-slate-800 hover:text-white"
                          }`
                        }
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-current opacity-40" />
                        {item.label}
                      </NavLink>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </nav>
      </aside>

      {sidebarOpen && <div className="fixed inset-0 bg-black/50 z-20 lg:hidden" onClick={() => setSidebarOpen(false)} />}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-4 lg:px-6 sticky top-0 z-10">
          <button className="lg:hidden p-2 hover:bg-slate-100 rounded-lg" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="flex items-center gap-3 ml-auto">
            <span className="text-xs px-2 py-1 rounded-full bg-indigo-50 text-indigo-600 font-medium capitalize">
              {user?.role}
            </span>
            <div className="text-right">
              <p className="text-sm font-medium text-slate-700">{user?.full_name || user?.username}</p>
              <p className="text-xs text-slate-400">{user?.role === "owner" ? "Egasi" : user?.role === "admin" ? "Admin" : "Kuzatuvchi"}</p>
            </div>
            <button onClick={handleLogout} className="p-2 hover:bg-red-50 rounded-lg text-slate-400 hover:text-red-600 transition-colors" title="Chiqish">
              <LogOut size={18} />
            </button>
          </div>
        </header>
        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export function StatCard({ title, value, icon: Icon, color = "indigo" }: { title: string; value: string | number; icon: any; color?: string }) {
  const colors: Record<string, string> = {
    indigo: "bg-indigo-50 text-indigo-600",
    emerald: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
    rose: "bg-rose-50 text-rose-600",
    blue: "bg-blue-50 text-blue-600",
    violet: "bg-violet-50 text-violet-600",
  };
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-800 mt-1">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors[color] || colors.indigo}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  );
}
