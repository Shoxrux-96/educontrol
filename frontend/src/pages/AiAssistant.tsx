import { useState, useEffect, useRef } from "react";
import { Bot, Send, Activity, AlertTriangle, CheckCircle, Wifi, Server, Monitor, MessageSquare, Lightbulb, Loader2 } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface Message {
  role: "user" | "ai";
  text: string;
  analysis?: {
    severity: "normal" | "warning" | "high";
    details?: string;
  };
}

interface AiStatus {
  status: "sog'lom" | "e'tibor talab" | "kritik";
  devices: number;
  computers: { online: number; total: number };
  traffic: string;
  ping: number;
  issues: { title: string; severity: string; description: string }[];
}

const suggestions = [
  "Nima uchun internet sekin?",
  "Tarmoq holati qanday?",
  "Qurilmalar ro'yxati",
  "Qanday muammolar bor?",
];

const severityColor: Record<string, string> = {
  normal: "bg-emerald-100 text-emerald-700",
  warning: "bg-amber-100 text-amber-700",
  high: "bg-rose-100 text-rose-700",
};

const statusColor: Record<string, string> = {
  "sog'lom": "bg-emerald-100 text-emerald-700 border-emerald-300",
  "e'tibor talab": "bg-amber-100 text-amber-700 border-amber-300",
  kritik: "bg-rose-100 text-rose-700 border-rose-300",
};

function formatText(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} className="font-semibold">{part.slice(2, -2)}</strong>;
    }
    const paragraphs = part.split("\n\n");
    return paragraphs.map((p, j) => (
      <p key={`${i}-${j}`} className={j > 0 ? "mt-2" : ""}>{p}</p>
    ));
  });
}

export default function AiAssistant() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [status, setStatus] = useState<AiStatus | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  useEffect(() => {
    api.get<AiStatus>("/ai/status")
      .then((r) => setStatus(r.data))
      .catch(() => {})
      .finally(() => setStatusLoading(false));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (question?: string) => {
    const q = (question || input).trim();
    if (!q || sending) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setSending(true);
    try {
      const { data } = await api.post<Message>("/ai/chat", { question: q });
      setMessages((prev) => [...prev, data]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "Kechirasiz, xatolik yuz berdi. Iltimos, qayta urinib ko'ring.", analysis: { severity: "high", details: "Server xatosi" } },
      ]);
    }
    setSending(false);
  };

  return (
    <div className="flex gap-4 h-[calc(100vh-6rem)]">
      {/* Left Panel - Chat */}
      <div className="w-[70%] flex flex-col bg-white rounded-xl border border-slate-200">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-slate-100">
          <div className="w-9 h-9 bg-indigo-100 rounded-xl flex items-center justify-center">
            <Bot size={20} className="text-indigo-600" />
          </div>
          <div>
            <h2 className="font-semibold text-slate-800">AI Yordamchi</h2>
            <p className="text-xs text-slate-400">Tarmoq va tizim boshqaruvi bo'yicha yordamchi</p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot size={48} className="text-slate-300 mb-4" />
              <p className="text-slate-400 mb-6">Assistentga savol berishingiz mumkin</p>
              <div className="flex flex-wrap gap-2 justify-center max-w-md">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSend(s)}
                    className="px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg text-slate-600 hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-600 transition-colors"
                  >
                    <Lightbulb size={14} className="inline mr-1.5 -mt-0.5" />
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] rounded-xl px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-sm"
                    : "bg-slate-50 border border-slate-200 text-slate-700 rounded-bl-sm"
                }`}
              >
                {msg.role === "ai" ? (
                  <div className="text-sm leading-relaxed">{formatText(msg.text)}</div>
                ) : (
                  <p className="text-sm">{msg.text}</p>
                )}
                {msg.analysis && (
                  <div className={`mt-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${severityColor[msg.analysis.severity] || severityColor.normal}`}>
                    {msg.analysis.severity === "high" ? <AlertTriangle size={12} /> : msg.analysis.severity === "warning" ? <Activity size={12} /> : <CheckCircle size={12} />}
                    {msg.analysis.severity === "normal" ? "Normal" : msg.analysis.severity === "warning" ? "E'tibor talab" : "Yuqori"}
                    {msg.analysis.details && ` - ${msg.analysis.details}`}
                  </div>
                )}
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex justify-start">
              <div className="bg-slate-50 border border-slate-200 rounded-xl rounded-bl-sm px-4 py-3">
                <Loader2 size={20} className="text-indigo-600 animate-spin" />
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <div className="px-5 py-4 border-t border-slate-100">
          <div className="flex gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), handleSend())}
              className="flex-1 px-4 py-2.5 border border-slate-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Savolingizni yozing..."
              rows={2}
            />
            <button
              onClick={() => handleSend()}
              disabled={sending || !input.trim()}
              className="self-end px-4 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Right Panel - Status */}
      <div className="w-[30%] bg-white rounded-xl border border-slate-200 p-5 overflow-y-auto">
        <div className="flex items-center gap-2 mb-5">
          <Activity size={20} className="text-indigo-600" />
          <h2 className="font-semibold text-slate-800">Tizim Holati</h2>
        </div>

        {statusLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600" />
          </div>
        ) : status ? (
          <>
            <div className={`p-4 rounded-xl border-2 mb-5 ${statusColor[status.status] || "bg-slate-50 text-slate-600 border-slate-200"}`}>
              <div className="flex items-center gap-2">
                {status.status === "kritik" ? <AlertTriangle size={20} /> : status.status === "e'tibor talab" ? <Activity size={20} /> : <CheckCircle size={20} />}
                <span className="font-semibold capitalize">{status.status}</span>
              </div>
            </div>

            <div className="space-y-3 mb-5">
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <Server size={18} className="text-slate-400" />
                <div className="flex-1">
                  <p className="text-xs text-slate-400">Qurilmalar</p>
                  <p className="font-semibold text-slate-700">{status.devices}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <Monitor size={18} className="text-slate-400" />
                <div className="flex-1">
                  <p className="text-xs text-slate-400">Kompyuterlar</p>
                  <p className="font-semibold text-slate-700">{status.computers.online}/{status.computers.total} online</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <Wifi size={18} className="text-slate-400" />
                <div className="flex-1">
                  <p className="text-xs text-slate-400">Traffic</p>
                  <p className="font-semibold text-slate-700">{status.traffic}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <Activity size={18} className="text-slate-400" />
                <div className="flex-1">
                  <p className="text-xs text-slate-400">Ping</p>
                  <p className="font-semibold text-slate-700">{status.ping} ms</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-1.5">
                <AlertTriangle size={16} className="text-amber-500" /> Muammolar
              </h3>
              <div className="space-y-2">
                {status.issues.length > 0 ? (
                  status.issues.map((issue, i) => (
                    <div key={i} className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`w-2 h-2 rounded-full ${issue.severity === "high" ? "bg-rose-500" : issue.severity === "warning" ? "bg-amber-500" : "bg-emerald-500"}`} />
                        <p className="text-sm font-medium text-slate-700">{issue.title}</p>
                      </div>
                      {issue.description && <p className="text-xs text-slate-400 ml-4">{issue.description}</p>}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-400 text-center py-4">Muammolar mavjud emas</p>
                )}
              </div>
            </div>
          </>
        ) : (
          <p className="text-sm text-slate-400 text-center py-8">Status ma'lumoti olinmadi</p>
        )}
      </div>
    </div>
  );
}
