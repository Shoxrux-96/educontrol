import { useState, useEffect } from "react";
import { Save, Database, Server, HardDrive, Clock, CheckCircle, XCircle, Play, RefreshCw, Plus, Pencil, Trash2, Archive } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface BackupJob {
  id: string;
  name: string;
  device_type: string;
  device_hostname: string;
  device_ip: string;
  backup_type: string;
  schedule_cron: string;
  retention_count: number;
  protocol: string;
  storage_path: string;
  username: string;
  last_run?: string;
  last_status: string;
  created_at: string;
}

interface BackupRecord {
  id: string;
  job_id: string;
  job_name: string;
  file_name: string;
  size_bytes: number;
  status: string;
  duration_seconds?: number;
  started_at?: string;
  completed_at?: string;
}

interface BackupSummary {
  total_jobs: number;
  active_jobs: number;
  completed_backups: number;
  storage_estimate_bytes: number;
}

interface JobForm {
  name: string;
  device_type: string;
  device_hostname: string;
  device_ip: string;
  backup_type: string;
  protocol: string;
  username: string;
  schedule_cron: string;
  retention_count: number;
  storage_path: string;
}

const emptyForm: JobForm = {
  name: "",
  device_type: "router",
  device_hostname: "",
  device_ip: "",
  backup_type: "config",
  protocol: "ssh",
  username: "",
  schedule_cron: "0 2 * * *",
  retention_count: 30,
  storage_path: "/backups",
};

const tabs = ["Backup Jobs", "Backup Records"];

const deviceTypes = ["router", "switch", "server", "firewall", "access_point"];
const backupTypes = ["config", "full", "firmware"];
const protocols = ["ssh", "telnet", "snmp", "https"];

function formatBytes(bytes: number) {
  if (!bytes) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

function statusBadge(status: string) {
  const m: Record<string, string> = {
    completed: "bg-emerald-100 text-emerald-700",
    failed: "bg-rose-100 text-rose-700",
    running: "bg-blue-100 text-blue-700",
    pending: "bg-slate-100 text-slate-500",
  };
  return m[status] || "bg-slate-100 text-slate-500";
}

export default function BackupManager() {
  const { isAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [jobs, setJobs] = useState<BackupJob[]>([]);
  const [records, setRecords] = useState<BackupRecord[]>([]);
  const [summary, setSummary] = useState<BackupSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<BackupJob | null>(null);
  const [form, setForm] = useState<JobForm>(emptyForm);
  const [recordJobFilter, setRecordJobFilter] = useState("");

  useEffect(() => {
    if (activeTab === 0) {
      fetchJobs();
      fetchSummary();
    } else {
      fetchRecords();
    }
  }, [activeTab]);

  const fetchSummary = async () => {
    try {
      const { data } = await api.get<BackupSummary>("/enterprise/backup/summary");
      setSummary(data);
    } catch { /* ignore */ }
  };

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<{ items: BackupJob[] }>("/enterprise/backup/jobs");
      setJobs(data.items || []);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { limit: "100" };
      if (recordJobFilter) params.job_id = recordJobFilter;
      const { data } = await api.get<{ items: BackupRecord[] }>("/enterprise/backup/records", { params });
      setRecords(data.items || []);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const openAdd = () => {
    setEditing(null);
    setForm(emptyForm);
    setShowModal(true);
  };

  const openEdit = (job: BackupJob) => {
    setEditing(job);
    setForm({
      name: job.name,
      device_type: job.device_type,
      device_hostname: job.device_hostname,
      device_ip: job.device_ip,
      backup_type: job.backup_type,
      protocol: job.protocol,
      username: job.username,
      schedule_cron: job.schedule_cron,
      retention_count: job.retention_count,
      storage_path: job.storage_path,
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    try {
      const payload = { ...form };
      if (editing) {
        await api.patch(`/enterprise/backup/jobs/${editing.id}`, payload);
      } else {
        await api.post("/enterprise/backup/jobs", payload);
      }
      setShowModal(false);
      fetchJobs();
    } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/enterprise/backup/jobs/${id}`);
      setJobs((prev) => prev.filter((j) => j.id !== id));
    } catch { /* ignore */ }
  };

  const handleRunNow = async (id: string) => {
    setRunning(id);
    try {
      await api.post(`/enterprise/backup/jobs/${id}/run`);
      fetchJobs();
    } catch { /* ignore */ }
    setRunning(null);
  };

  const summaryCards = summary ? [
    { label: "Total Jobs", value: summary.total_jobs, icon: Database, color: "bg-indigo-50 text-indigo-600" },
    { label: "Active Jobs", value: summary.active_jobs, icon: Clock, color: "bg-blue-50 text-blue-600" },
    { label: "Completed Backups", value: summary.completed_backups, icon: CheckCircle, color: "bg-emerald-50 text-emerald-600" },
    { label: "Storage Estimate", value: formatBytes(summary.storage_estimate_bytes), icon: HardDrive, color: "bg-amber-50 text-amber-600" },
  ] : [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Backup Manager</h1>
        {activeTab === 0 && (
          <button onClick={openAdd}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
            <Plus size={16} /> Add Job
          </button>
        )}
      </div>

      {summaryCards.length > 0 && activeTab === 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {summaryCards.map((card) => (
            <div key={card.label} className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${card.color}`}>
                <card.icon size={20} />
              </div>
              <div>
                <p className="text-xs text-slate-500">{card.label}</p>
                <p className="text-lg font-bold text-slate-800">{card.value}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-1 mb-6 border-b border-slate-200">
        {tabs.map((tab, i) => (
          <button key={tab} onClick={() => setActiveTab(i)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === i
                ? "border-indigo-600 text-indigo-600"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}>
            {tab}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading...</div>
      ) : (
        <>
          {activeTab === 0 && (
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                      <th className="text-left px-4 py-3 font-medium">Name</th>
                      <th className="text-left px-4 py-3 font-medium">Device</th>
                      <th className="text-left px-4 py-3 font-medium">Type</th>
                      <th className="text-left px-4 py-3 font-medium">Schedule</th>
                      <th className="text-left px-4 py-3 font-medium">Retention</th>
                      <th className="text-left px-4 py-3 font-medium">Protocol</th>
                      <th className="text-left px-4 py-3 font-medium">Last Run</th>
                      <th className="text-left px-4 py-3 font-medium">Status</th>
                      <th className="text-right px-4 py-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {jobs.map((job) => (
                      <tr key={job.id} className="hover:bg-slate-50">
                        <td className="px-4 py-3 font-medium text-slate-800">{job.name}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <Server size={14} className="text-slate-400" />
                            <span className="text-xs text-slate-600">{job.device_type}</span>
                            <span className="text-xs text-slate-400">{job.device_hostname || job.device_ip}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
                            {job.backup_type}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-mono text-xs text-slate-500">{job.schedule_cron}</td>
                        <td className="px-4 py-3 text-slate-600">{job.retention_count}</td>
                        <td className="px-4 py-3 text-xs text-slate-500 uppercase">{job.protocol}</td>
                        <td className="px-4 py-3 text-xs text-slate-400">
                          {job.last_run ? new Date(job.last_run).toLocaleString() : "—"}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${statusBadge(job.last_status)}`}>
                            {job.last_status === "running" && <RefreshCw size={12} className="animate-spin" />}
                            {job.last_status === "completed" && <CheckCircle size={12} />}
                            {job.last_status === "failed" && <XCircle size={12} />}
                            {job.last_status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button onClick={() => handleRunNow(job.id)} disabled={running === job.id}
                            className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg disabled:opacity-50"
            title="Run now">
                            {running === job.id ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />}
                          </button>
                          <button onClick={() => openEdit(job)} className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg ml-1" title="Edit">
                            <Pencil size={14} />
                          </button>
                          <button onClick={() => handleDelete(job.id)} className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg ml-1" title="Delete">
                            <Trash2 size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {jobs.length === 0 && <div className="text-center py-12 text-slate-400">No backup jobs found</div>}
            </div>
          )}

          {activeTab === 1 && (
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <div className="p-4 border-b border-slate-200 flex items-center gap-3">
                <Archive size={16} className="text-slate-400" />
                <select value={recordJobFilter} onChange={(e) => { setRecordJobFilter(e.target.value); }}
                  className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="">All Jobs</option>
                  {jobs.map((j) => (
                    <option key={j.id} value={j.id}>{j.name}</option>
                  ))}
                </select>
                <button onClick={fetchRecords}
                  className="flex items-center gap-1 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">
                  <RefreshCw size={14} /> Refresh
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                      <th className="text-left px-4 py-3 font-medium">File Name</th>
                      <th className="text-left px-4 py-3 font-medium">Job</th>
                      <th className="text-left px-4 py-3 font-medium">Size</th>
                      <th className="text-left px-4 py-3 font-medium">Status</th>
                      <th className="text-left px-4 py-3 font-medium">Duration</th>
                      <th className="text-left px-4 py-3 font-medium">Started</th>
                      <th className="text-left px-4 py-3 font-medium">Completed</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {records.map((rec) => (
                      <tr key={rec.id} className="hover:bg-slate-50">
                        <td className="px-4 py-3 font-mono text-xs text-slate-800">{rec.file_name}</td>
                        <td className="px-4 py-3 text-slate-600">{rec.job_name}</td>
                        <td className="px-4 py-3 text-slate-600">{formatBytes(rec.size_bytes)}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${statusBadge(rec.status)}`}>
                            {rec.status === "running" && <RefreshCw size={12} className="animate-spin" />}
                            {rec.status === "completed" && <CheckCircle size={12} />}
                            {rec.status === "failed" && <XCircle size={12} />}
                            {rec.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-500">
                          {rec.duration_seconds ? `${rec.duration_seconds}s` : "—"}
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-400">
                          {rec.started_at ? new Date(rec.started_at).toLocaleString() : "—"}
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-400">
                          {rec.completed_at ? new Date(rec.completed_at).toLocaleString() : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {records.length === 0 && <div className="text-center py-12 text-slate-400">No backup records found</div>}
            </div>
          )}
        </>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">{editing ? "Edit Backup Job" : "Add Backup Job"}</h2>
              <button onClick={() => setShowModal(false)} className="p-1 text-slate-400 hover:text-slate-600"><XCircle size={18} /></button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Name</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Device Type</label>
                  <select value={form.device_type} onChange={(e) => setForm({ ...form, device_type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    {deviceTypes.map((dt) => (
                      <option key={dt} value={dt}>{dt}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Backup Type</label>
                  <select value={form.backup_type} onChange={(e) => setForm({ ...form, backup_type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    {backupTypes.map((bt) => (
                      <option key={bt} value={bt}>{bt}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Device Hostname</label>
                <input type="text" value={form.device_hostname} onChange={(e) => setForm({ ...form, device_hostname: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Device IP</label>
                <input type="text" value={form.device_ip} onChange={(e) => setForm({ ...form, device_ip: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Protocol</label>
                  <select value={form.protocol} onChange={(e) => setForm({ ...form, protocol: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    {protocols.map((p) => (
                      <option key={p} value={p}>{p.toUpperCase()}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Username</label>
                  <input type="text" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Schedule (Cron)</label>
                <input type="text" value={form.schedule_cron} onChange={(e) => setForm({ ...form, schedule_cron: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Retention Count</label>
                  <input type="number" value={form.retention_count} onChange={(e) => setForm({ ...form, retention_count: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Storage Path</label>
                  <input type="text" value={form.storage_path} onChange={(e) => setForm({ ...form, storage_path: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono" />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
              <button onClick={handleSave} className="flex items-center gap-2 px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                <Save size={14} /> {editing ? "Save" : "Add"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
