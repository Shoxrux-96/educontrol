import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Settings, Database, LogIn, RefreshCw, CheckCircle, XCircle, Users, Layers, FolderTree } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface ADConfig {
  domain_name: string;
  domain_controller: string;
  ldap_base_dn: string;
  ldap_user: string;
  ldap_password: string;
  use_ssl: boolean;
  sync_interval_minutes: number;
  sso_enabled: boolean;
  auto_create_users: boolean;
  default_role: string;
}

interface ADUser {
  sam_account_name: string;
  display_name: string;
  email: string;
  ou: string;
  enabled: boolean;
  linked: boolean;
}

interface ADGroup {
  name: string;
  sam_account_name: string;
  member_count: number;
}

interface ADOU {
  name: string;
  distinguished_name: string;
  user_count: number;
  computer_count: number;
}

interface SyncResult {
  users: number;
  groups: number;
  ous: number;
}

const defaultConfig: ADConfig = {
  domain_name: "",
  domain_controller: "",
  ldap_base_dn: "",
  ldap_user: "",
  ldap_password: "",
  use_ssl: false,
  sync_interval_minutes: 60,
  sso_enabled: false,
  auto_create_users: false,
  default_role: "viewer",
};

export default function ActiveDirectory() {
  const [activeTab, setActiveTab] = useState(0);
  const tabs = [
    { label: "Domain sozlamalari", icon: Settings },
    { label: "Import qilingan ma'lumotlar", icon: Database },
    { label: "SSO", icon: LogIn },
  ];

  return (
    <div>
      <h1 className="text-xl font-bold text-slate-800 mb-6">Active Directory</h1>
      <div className="flex gap-1 bg-slate-100 rounded-lg p-1 mb-6">
        {tabs.map((t, i) => (
          <button
            key={i}
            onClick={() => setActiveTab(i)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === i ? "bg-white text-indigo-600 shadow-sm" : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <t.icon size={16} /> {t.label}
          </button>
        ))}
      </div>
      {activeTab === 0 && <DomainSettings />}
      {activeTab === 1 && <ImportedData />}
      {activeTab === 2 && <SSOTab />}
    </div>
  );
}

function DomainSettings() {
  const [config, setConfig] = useState<ADConfig>(defaultConfig);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [testMsg, setTestMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get<ADConfig>("/ad/config").then((r) => r.data && setConfig(r.data)).catch(() => {});
  }, []);

  const update = (key: keyof ADConfig, value: string | boolean | number) =>
    setConfig((prev) => ({ ...prev, [key]: value }));

  const save = async () => {
    setSaving(true);
    try {
      await api.post("/ad/config", config);
    } catch {
      /* ignore */
    }
    setSaving(false);
  };

  const testConnection = async () => {
    setTestMsg(null);
    try {
      await api.post("/ad/config/test", config);
      setTestMsg({ ok: true, text: "Ulanish muvaffaqiyatli" });
    } catch {
      setTestMsg({ ok: false, text: "Ulanishda xatolik yuz berdi" });
    }
  };

  const syncNow = async () => {
    setSyncResult(null);
    try {
      const { data } = await api.post<SyncResult>("/ad/config/sync", config);
      setSyncResult(data);
    } catch {
      /* ignore */
    }
  };

  const syncStatusBadge = config.domain_name
    ? "bg-emerald-100 text-emerald-700"
    : "bg-slate-100 text-slate-500";

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-5">
        <h2 className="font-semibold text-slate-800">Domain ulanish sozlamalari</h2>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${syncStatusBadge}`}>
          {config.domain_name ? "Sozlangan" : "Sozlanmagan"}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Domain Name</label>
          <input
            type="text" value={config.domain_name}
            onChange={(e) => update("domain_name", e.target.value)}
            className="w-full border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 px-4 py-2"
            placeholder="school.local"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Domain Controller</label>
          <input
            type="text" value={config.domain_controller}
            onChange={(e) => update("domain_controller", e.target.value)}
            className="w-full border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 px-4 py-2"
            placeholder="dc01.school.local"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">LDAP Base DN</label>
          <input
            type="text" value={config.ldap_base_dn}
            onChange={(e) => update("ldap_base_dn", e.target.value)}
            className="w-full border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 px-4 py-2"
            placeholder="DC=school,DC=local"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">LDAP User</label>
          <input
            type="text" value={config.ldap_user}
            onChange={(e) => update("ldap_user", e.target.value)}
            className="w-full border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 px-4 py-2"
            placeholder="ixtiyoriy"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">LDAP Password</label>
          <input
            type="password" value={config.ldap_password}
            onChange={(e) => update("ldap_password", e.target.value)}
            className="w-full border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 px-4 py-2"
            placeholder="ixtiyoriy"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Sync Interval (min)</label>
          <input
            type="number" value={config.sync_interval_minutes}
            onChange={(e) => update("sync_interval_minutes", Number(e.target.value))}
            className="w-full border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 px-4 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Default Role</label>
          <select
            value={config.default_role}
            onChange={(e) => update("default_role", e.target.value)}
            className="w-full border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 px-4 py-2"
          >
            <option value="viewer">Viewer</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <div className="flex items-end gap-6 pb-2">
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" checked={config.use_ssl} onChange={(e) => update("use_ssl", e.target.checked)}
              className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
            Use SSL
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" checked={config.sso_enabled} onChange={(e) => update("sso_enabled", e.target.checked)}
              className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
            SSO Enabled
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" checked={config.auto_create_users} onChange={(e) => update("auto_create_users", e.target.checked)}
              className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
            Auto Create Users
          </label>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button onClick={save} disabled={saving}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
          {saving ? "Saqlanmoqda..." : "Saqlash"}
        </button>
        <button onClick={testConnection}
          className="px-4 py-2 border border-slate-200 text-slate-700 rounded-lg text-sm hover:bg-slate-50">
          Test Connection
        </button>
        <button onClick={syncNow}
          className="flex items-center gap-2 px-4 py-2 border border-slate-200 text-slate-700 rounded-lg text-sm hover:bg-slate-50">
          <RefreshCw size={16} /> Sync Now
        </button>
      </div>

      {testMsg && (
        <div className={`flex items-center gap-2 mt-4 text-sm ${testMsg.ok ? "text-emerald-600" : "text-rose-600"}`}>
          {testMsg.ok ? <CheckCircle size={16} /> : <XCircle size={16} />}
          {testMsg.text}
        </div>
      )}

      {syncResult && (
        <div className="mt-4 p-4 bg-slate-50 rounded-lg text-sm text-slate-700">
          <p className="font-medium mb-1">Sinxronizatsiya natijasi:</p>
          <p>{syncResult.users} foydalanuvchi, {syncResult.groups} guruh, {syncResult.ous} OU</p>
        </div>
      )}
    </div>
  );
}

function ImportedData() {
  const [subTab, setSubTab] = useState(0);
  const [users, setUsers] = useState<ADUser[]>([]);
  const [groups, setGroups] = useState<ADGroup[]>([]);
  const [ous, setOus] = useState<ADOU[]>([]);
  const [loading, setLoading] = useState(false);

  const subTabs = [
    { label: "Foydalanuvchilar", icon: Users },
    { label: "Guruhlar", icon: Layers },
    { label: "OU lar", icon: FolderTree },
  ];

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get<ADUser[]>("/ad/users").then((r) => setUsers(r.data)).catch(() => {}),
      api.get<ADGroup[]>("/ad/groups").then((r) => setGroups(r.data)).catch(() => {}),
      api.get<ADOU[]>("/ad/ous").then((r) => setOus(r.data)).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <div className="flex gap-1 bg-slate-100 rounded-lg p-1 mb-5">
        {subTabs.map((t, i) => (
          <button
            key={i}
            onClick={() => setSubTab(i)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              subTab === i ? "bg-white text-indigo-600 shadow-sm" : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <t.icon size={16} /> {t.label}
          </button>
        ))}
      </div>

      {loading && <div className="text-center py-8 text-slate-400">Yuklanmoqda...</div>}

      {subTab === 0 && !loading && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="pb-3 font-medium">SAM Account Name</th>
                <th className="pb-3 font-medium">Display Name</th>
                <th className="pb-3 font-medium">Email</th>
                <th className="pb-3 font-medium">OU</th>
                <th className="pb-3 font-medium">Holati</th>
                <th className="pb-3 font-medium">Bog'langan</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u, i) => (
                <tr key={i} className="border-b border-slate-100 text-slate-700">
                  <td className="py-3">{u.sam_account_name}</td>
                  <td className="py-3">{u.display_name}</td>
                  <td className="py-3">{u.email}</td>
                  <td className="py-3">{u.ou}</td>
                  <td className="py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.enabled ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                      {u.enabled ? "Faol" : "Bloklangan"}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.linked ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-500"}`}>
                      {u.linked ? "Bog'langan" : "Bog'lanmagan"}
                    </span>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr><td colSpan={6} className="py-8 text-center text-slate-400">Foydalanuvchilar topilmadi</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {subTab === 1 && !loading && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="pb-3 font-medium">Nomi</th>
                <th className="pb-3 font-medium">SAM Account Name</th>
                <th className="pb-3 font-medium">A'zolar soni</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((g, i) => (
                <tr key={i} className="border-b border-slate-100 text-slate-700">
                  <td className="py-3">{g.name}</td>
                  <td className="py-3">{g.sam_account_name}</td>
                  <td className="py-3">{g.member_count}</td>
                </tr>
              ))}
              {groups.length === 0 && (
                <tr><td colSpan={3} className="py-8 text-center text-slate-400">Guruhlar topilmadi</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {subTab === 2 && !loading && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="pb-3 font-medium">Nomi</th>
                <th className="pb-3 font-medium">Distinguished Name</th>
                <th className="pb-3 font-medium">Foydalanuvchilar</th>
                <th className="pb-3 font-medium">Kompyuterlar</th>
              </tr>
            </thead>
            <tbody>
              {ous.map((o, i) => (
                <tr key={i} className="border-b border-slate-100 text-slate-700">
                  <td className="py-3">{o.name}</td>
                  <td className="py-3">{o.distinguished_name}</td>
                  <td className="py-3">{o.user_count}</td>
                  <td className="py-3">{o.computer_count}</td>
                </tr>
              ))}
              {ous.length === 0 && (
                <tr><td colSpan={4} className="py-8 text-center text-slate-400">OU lar topilmadi</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function SSOTab() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [ssoEnabled, setSsoEnabled] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get<ADConfig>("/ad/config").then((r) => setSsoEnabled(r.data.sso_enabled)).catch(() => {});
  }, []);

  const handleSSOLogin = async () => {
    setError("");
    try {
      const { data } = await api.post<{ access_token: string; user: { username: string; role: string } }>("/ad/sso/login", { username, password });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/dashboard");
    } catch {
      setError("Login yoki parol noto'g'ri");
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <div className="flex items-center gap-3 mb-5">
        <h2 className="font-semibold text-slate-800">SSO (Single Sign-On)</h2>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${ssoEnabled ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
          {ssoEnabled ? "Faol" : "No faol"}
        </span>
      </div>

      <p className="text-sm text-slate-500 mb-5">Bir marta login bilan barcha tizimlarga kiring</p>

      <div className="max-w-sm space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}
            className="w-full border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 px-4 py-2"
            placeholder="domain\username" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 px-4 py-2"
            placeholder="••••••••" />
        </div>
        {error && <p className="text-sm text-rose-600">{error}</p>}
        <button onClick={handleSSOLogin}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
          <LogIn size={16} /> Domain orqali kirish
        </button>
      </div>
    </div>
  );
}
