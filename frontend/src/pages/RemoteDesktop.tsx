import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Monitor, Mouse, Keyboard, Power, PowerOff, RotateCcw, Moon, Wifi, Play, Square, Loader2 } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";
import type { Computer } from "../types";

interface RemoteSession {
  id: string;
  computer_id: string;
  computer_name: string;
  status: string;
  started_at: string;
}

export default function RemoteDesktop() {
  const { computerId } = useParams<{ computerId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [computer, setComputer] = useState<Computer | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionActive, setSessionActive] = useState(false);
  const [activeSessions, setActiveSessions] = useState<RemoteSession[]>([]);
  const [loadingComputer, setLoadingComputer] = useState(true);
  const [startingSession, setStartingSession] = useState(false);
  const [stoppingSession, setStoppingSession] = useState(false);
  const [screenshotLoading, setScreenshotLoading] = useState(false);
  const [screenshotMsg, setScreenshotMsg] = useState("");
  const [mouseLoading, setMouseLoading] = useState(false);
  const [keyboardText, setKeyboardText] = useState("");
  const [keyboardLoading, setKeyboardLoading] = useState(false);
  const [powerLoading, setPowerLoading] = useState<string | null>(null);
  const [powerMsg, setPowerMsg] = useState("");

  useEffect(() => {
    if (!computerId) return;
    (async () => {
      try {
        const { data } = await api.get<Computer>(`/computers/${computerId}`);
        setComputer(data);
      } catch {}
      setLoadingComputer(false);
    })();
  }, [computerId]);

  useEffect(() => {
    fetchActiveSessions();
    const iv = setInterval(fetchActiveSessions, 15000);
    return () => clearInterval(iv);
  }, []);

  const fetchActiveSessions = async () => {
    try {
      const { data } = await api.get<RemoteSession[]>("/computers/remote/active");
      setActiveSessions(data);
      const match = data.find((s) => s.computer_id === computerId);
      if (match) {
        setSessionId(match.id);
        setSessionActive(match.status === "active");
      }
    } catch {}
  };

  const startSession = async () => {
    if (!computerId) return;
    setStartingSession(true);
    try {
      const { data } = await api.post<{ session_id: string }>(`/computers/${computerId}/remote/start`);
      setSessionId(data.session_id);
      setSessionActive(true);
    } catch {}
    setStartingSession(false);
  };

  const stopSession = async () => {
    if (!sessionId) return;
    setStoppingSession(true);
    try {
      await api.post(`/computers/remote/${sessionId}/stop`);
      setSessionActive(false);
      setSessionId(null);
    } catch {}
    setStoppingSession(false);
  };

  const takeScreenshot = async () => {
    if (!computerId) return;
    setScreenshotLoading(true);
    setScreenshotMsg("");
    try {
      await api.post(`/computers/${computerId}/remote/screenshot`);
      setScreenshotMsg("Screenshot saqlandi");
    } catch {
      setScreenshotMsg("Xatolik yuz berdi");
    }
    setScreenshotLoading(false);
    setTimeout(() => setScreenshotMsg(""), 3000);
  };

  const sendMouseInput = async (action: string) => {
    if (!computerId) return;
    setMouseLoading(true);
    try {
      await api.post(`/computers/${computerId}/remote/input`, {
        type: "mouse",
        data: { action },
      });
    } catch {}
    setMouseLoading(false);
  };

  const sendKeyboardInput = async () => {
    if (!computerId || !keyboardText.trim()) return;
    setKeyboardLoading(true);
    try {
      await api.post(`/computers/${computerId}/remote/input`, {
        type: "keyboard",
        data: { text: keyboardText },
      });
      setKeyboardText("");
    } catch {}
    setKeyboardLoading(false);
  };

  const sendPowerAction = async (action: string) => {
    if (!computerId) return;
    setPowerLoading(action);
    setPowerMsg("");
    try {
      await api.post(`/computers/${computerId}/power`, { action });
      setPowerMsg(`${action} so'rovi yuborildi`);
    } catch {
      setPowerMsg("Xatolik yuz berdi");
    }
    setPowerLoading(null);
    setTimeout(() => setPowerMsg(""), 3000);
  };

  if (loadingComputer) {
    return <div className="text-center py-12 text-slate-400">Yuklanmoqda...</div>;
  }

  if (!computer) {
    return <div className="text-center py-12 text-slate-400">Kompyuter topilmadi</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">
          Remote Desktop — {computer.name}
        </h1>
      </div>

      <div className="flex items-center gap-4 bg-white rounded-xl border border-slate-200 px-5 py-4">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center shrink-0">
            <Monitor size={20} className="text-slate-600" />
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-slate-800 truncate">{computer.name}</p>
            <p className="text-xs text-slate-400">{computer.ip_address || computer.hostname || "IP noma'lum"}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 ml-auto">
          <span className={`w-3 h-3 rounded-full ${sessionActive ? "bg-emerald-500" : "bg-slate-300"}`} />
          <span className="text-sm text-slate-600">{sessionActive ? "Session active" : "Session closed"}</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={startSession}
            disabled={startingSession || sessionActive}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg transition-colors"
          >
            {startingSession ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
            Start Session
          </button>
          <button
            onClick={stopSession}
            disabled={stoppingSession || !sessionActive}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 rounded-lg transition-colors"
          >
            {stoppingSession ? <Loader2 size={14} className="animate-spin" /> : <Square size={14} />}
            Stop Session
          </button>
        </div>
      </div>

      <div className="flex gap-6">
        <div className="flex-1 space-y-6">
          <div className="relative bg-slate-900 rounded-xl border border-slate-700 overflow-hidden" style={{ width: 1024, height: 768 }}>
            <div
              className="absolute inset-0 opacity-10"
              style={{
                backgroundImage:
                  "linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)",
                backgroundSize: "40px 40px",
              }}
            />
            <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
              <Monitor size={64} className="mb-4 opacity-40" />
              <p className="text-lg font-medium">Ekran ko'rinishi</p>
              <p className="text-sm mt-1 opacity-60">Remote desktop ekran bu yerda ko'rsatiladi</p>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <button
              onClick={takeScreenshot}
              disabled={screenshotLoading}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 disabled:opacity-50 rounded-lg transition-colors"
            >
              {screenshotLoading ? <Loader2 size={14} className="animate-spin" /> : <Monitor size={14} />}
              Screenshot olish
            </button>
            {screenshotMsg && (
              <span className="text-sm text-emerald-600">{screenshotMsg}</span>
            )}
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <Mouse size={16} /> Sichqoncha boshqaruvi
            </h3>
            <div className="flex items-center gap-3">
              <div className="grid grid-cols-3 gap-2">
                <div />
                <button
                  onClick={() => sendMouseInput("up")}
                  disabled={mouseLoading}
                  className="w-10 h-10 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 rounded-lg flex items-center justify-center text-slate-600 text-sm font-medium transition-colors"
                >
                  ↑
                </button>
                <div />
                <button
                  onClick={() => sendMouseInput("left")}
                  disabled={mouseLoading}
                  className="w-10 h-10 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 rounded-lg flex items-center justify-center text-slate-600 text-sm font-medium transition-colors"
                >
                  ←
                </button>
                <button
                  onClick={() => sendMouseInput("click")}
                  disabled={mouseLoading}
                  className="w-10 h-10 bg-indigo-100 hover:bg-indigo-200 disabled:opacity-50 rounded-lg flex items-center justify-center text-indigo-600 text-sm font-medium transition-colors"
                >
                  Click
                </button>
                <button
                  onClick={() => sendMouseInput("right")}
                  disabled={mouseLoading}
                  className="w-10 h-10 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 rounded-lg flex items-center justify-center text-slate-600 text-sm font-medium transition-colors"
                >
                  →
                </button>
                <div />
                <button
                  onClick={() => sendMouseInput("down")}
                  disabled={mouseLoading}
                  className="w-10 h-10 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 rounded-lg flex items-center justify-center text-slate-600 text-sm font-medium transition-colors"
                >
                  ↓
                </button>
                <div />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <Keyboard size={16} /> Klaviatura
            </h3>
            <div className="flex gap-3">
              <input
                type="text"
                value={keyboardText}
                onChange={(e) => setKeyboardText(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") sendKeyboardInput(); }}
                placeholder="Matn kiriting..."
                className="flex-1 px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                onClick={sendKeyboardInput}
                disabled={keyboardLoading || !keyboardText.trim()}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg transition-colors"
              >
                {keyboardLoading ? <Loader2 size={14} className="animate-spin" /> : <Keyboard size={14} />}
                Yuborish
              </button>
            </div>
          </div>
        </div>

        <div className="w-64 shrink-0 space-y-3">
          <h3 className="font-semibold text-slate-800">Quvvatni boshqarish</h3>

          <button
            onClick={() => sendPowerAction("shutdown")}
            disabled={powerLoading === "shutdown"}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:opacity-50 rounded-xl transition-colors"
          >
            {powerLoading === "shutdown" ? <Loader2 size={16} className="animate-spin" /> : <PowerOff size={16} />}
            Shutdown
          </button>

          <button
            onClick={() => sendPowerAction("restart")}
            disabled={powerLoading === "restart"}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-white bg-amber-500 hover:bg-amber-600 disabled:opacity-50 rounded-xl transition-colors"
          >
            {powerLoading === "restart" ? <Loader2 size={16} className="animate-spin" /> : <RotateCcw size={16} />}
            Restart
          </button>

          <button
            onClick={() => sendPowerAction("sleep")}
            disabled={powerLoading === "sleep"}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-xl transition-colors"
          >
            {powerLoading === "sleep" ? <Loader2 size={16} className="animate-spin" /> : <Moon size={16} />}
            Sleep
          </button>

          <button
            onClick={() => sendPowerAction("wake")}
            disabled={powerLoading === "wake"}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 rounded-xl transition-colors"
          >
            {powerLoading === "wake" ? <Loader2 size={16} className="animate-spin" /> : <Wifi size={16} />}
            Wake On LAN
          </button>

          {powerMsg && (
            <div className="text-sm text-center text-emerald-600 bg-emerald-50 px-3 py-2 rounded-lg">{powerMsg}</div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-200">
          <h2 className="font-semibold text-slate-800">Active Sessions</h2>
        </div>
        <div className="p-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 text-xs uppercase tracking-wider">
                <th className="text-left pb-3 font-medium">Kompyuter</th>
                <th className="text-left pb-3 font-medium">Holat</th>
                <th className="text-left pb-3 font-medium">Boshlangan vaqt</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {activeSessions.map((s) => (
                <tr key={s.id} className="text-slate-700">
                  <td className="py-3 font-medium">{s.computer_name}</td>
                  <td className="py-3">
                    <span className={`flex items-center gap-1.5 ${s.status === "active" ? "text-emerald-600" : "text-slate-400"}`}>
                      <span className={`w-2 h-2 rounded-full ${s.status === "active" ? "bg-emerald-500" : "bg-slate-300"}`} />
                      {s.status}
                    </span>
                  </td>
                  <td className="py-3 text-slate-500">{new Date(s.started_at).toLocaleString("uz-UZ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {activeSessions.length === 0 && (
            <p className="text-center py-6 text-slate-400">Faol sessiyalar mavjud emas</p>
          )}
        </div>
      </div>
    </div>
  );
}
