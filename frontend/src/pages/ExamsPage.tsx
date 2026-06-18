import { useState, useEffect } from "react";
import { BookOpen, CheckCircle, XCircle, Play, Square, Shield, Globe, Monitor, Terminal, Mouse, Send, MessageSquare, AlertTriangle, Users, Plus, Trash2, Search, Pencil } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../api/AuthContext";

interface Exam {
  id: string;
  name: string;
  subject?: string;
  description?: string;
  status: "scheduled" | "active" | "completed" | "cancelled";
  duration_minutes: number;
  block_internet: boolean;
  block_usb: boolean;
  block_alt_tab: boolean;
  block_task_manager: boolean;
  block_cmd: boolean;
  monitor_screens: boolean;
  auto_submit_on_leave: boolean;
  participants_count?: number;
  created_at: string;
}

interface ExamForm {
  name: string;
  description: string;
  subject: string;
  duration_minutes: number;
  block_internet: boolean;
  block_usb: boolean;
  block_alt_tab: boolean;
  block_task_manager: boolean;
  block_cmd: boolean;
  monitor_screens: boolean;
  auto_submit_on_leave: boolean;
  computer_ids: string[];
}

interface Question {
  id: string;
  question_type: "single" | "multiple" | "text" | "true_false";
  question_text: string;
  options?: Record<string, string>;
  correct_answer?: string;
  points: number;
  category?: string;
  created_at: string;
}

interface QuestionForm {
  question_type: string;
  question_text: string;
  options: string;
  correct_answer: string;
  points: number;
  category: string;
}

interface Participant {
  id: string;
  student_name: string;
  computer_name: string;
  computer_id: string;
  status: "pending" | "active" | "completed";
  violations: number;
  is_blocked: boolean;
}

interface ActivityLog {
  id: string;
  event: string;
  computer_name?: string;
  student_name?: string;
  created_at: string;
}

interface Computer {
  id: string;
  name: string;
  ip_address?: string;
}

const STATUS_COLORS: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-700",
  active: "bg-emerald-100 text-emerald-700",
  completed: "bg-slate-100 text-slate-500",
  cancelled: "bg-rose-100 text-rose-700",
};

const STATUS_LABELS: Record<string, string> = {
  scheduled: "Rejalashtirilgan",
  active: "Faol",
  completed: "Yakunlangan",
  cancelled: "Bekor qilingan",
};

const QUESTION_TYPE_LABELS: Record<string, string> = {
  single: "Bir tanlov",
  multiple: "Ko'p tanlov",
  text: "Matn",
  true_false: "To'g'ri/Noto'g'ri",
};

const emptyExamForm: ExamForm = {
  name: "", description: "", subject: "", duration_minutes: 60,
  block_internet: false, block_usb: false, block_alt_tab: false,
  block_task_manager: false, block_cmd: false,
  monitor_screens: false, auto_submit_on_leave: false,
  computer_ids: [],
};

const emptyQuestionForm: QuestionForm = {
  question_type: "single", question_text: "", options: "{}",
  correct_answer: "", points: 1, category: "",
};

export default function ExamsPage() {
  const [activeTab, setActiveTab] = useState(0);
  const { isAdmin } = useAuth();

  // Tab 1: Exams
  const [exams, setExams] = useState<Exam[]>([]);
  const [examsLoading, setExamsLoading] = useState(true);
  const [examActionLoading, setExamActionLoading] = useState<string | null>(null);

  // Tab 2: New Exam
  const [examForm, setExamForm] = useState<ExamForm>(emptyExamForm);
  const [computers, setComputers] = useState<Computer[]>([]);
  const [savingExam, setSavingExam] = useState(false);

  // Tab 3: Questions
  const [questions, setQuestions] = useState<Question[]>([]);
  const [questionsLoading, setQuestionsLoading] = useState(true);
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [questionForm, setQuestionForm] = useState<QuestionForm>(emptyQuestionForm);
  const [savingQuestion, setSavingQuestion] = useState(false);

  // Tab 4: Live Monitoring
  const [monitorExamId, setMonitorExamId] = useState<string>("");
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [messageText, setMessageText] = useState("");
  const [messageComputers, setMessageComputers] = useState<string[]>([]);
  const [testExamQuestions, setTestExamQuestions] = useState<string[]>([]);
  const [testComputers, setTestComputers] = useState<string[]>([]);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [sendingTest, setSendingTest] = useState(false);

  const tabs = ["Imtihonlar", "Yangi imtihon", "Test savollari", "Jonli monitoring"];

  useEffect(() => {
    fetchExams();
    fetchQuestions();
    fetchComputers();
    fetchActivity();
  }, []);

  const fetchExams = async () => {
    setExamsLoading(true);
    try {
      const { data } = await api.get<Exam[]>("/education/exams");
      setExams(Array.isArray(data) ? data : []);
    } catch { /* ignore */ }
    setExamsLoading(false);
  };

  const fetchQuestions = async () => {
    setQuestionsLoading(true);
    try {
      const { data } = await api.get<Question[]>("/education/questions");
      setQuestions(Array.isArray(data) ? data : []);
    } catch { /* ignore */ }
    setQuestionsLoading(false);
  };

  const fetchComputers = async () => {
    try {
      const { data } = await api.get<{ items: Computer[] }>("/computers?page_size=200");
      setComputers(data.items || []);
    } catch { /* ignore */ }
  };

  const fetchParticipants = async (examId: string) => {
    try {
      const { data } = await api.get<Participant[]>(`/education/exams/${examId}/participants`);
      setParticipants(Array.isArray(data) ? data : []);
    } catch { /* ignore */ }
  };

  const fetchActivity = async () => {
    try {
      const { data } = await api.get<ActivityLog[]>("/education/activity");
      setActivityLogs(Array.isArray(data) ? data : []);
    } catch { /* ignore */ }
  };

  const handleExamAction = async (examId: string, action: "start" | "stop") => {
    setExamActionLoading(`${examId}-${action}`);
    try {
      await api.post(`/education/exams/${examId}/${action}`);
      fetchExams();
    } catch { /* ignore */ }
    setExamActionLoading(null);
  };

  const handleDeleteExam = async (examId: string) => {
    try {
      await api.delete(`/education/exams/${examId}`);
      fetchExams();
    } catch { /* ignore */ }
  };

  const handleSaveExam = async () => {
    setSavingExam(true);
    try {
      const { data } = await api.post<Exam>("/education/exams", {
        name: examForm.name,
        description: examForm.description || undefined,
        subject: examForm.subject || undefined,
        duration_minutes: examForm.duration_minutes,
        block_internet: examForm.block_internet,
        block_usb: examForm.block_usb,
        block_alt_tab: examForm.block_alt_tab,
        block_task_manager: examForm.block_task_manager,
        block_cmd: examForm.block_cmd,
        monitor_screens: examForm.monitor_screens,
        auto_submit_on_leave: examForm.auto_submit_on_leave,
      });
      if (examForm.computer_ids.length > 0) {
        await api.post(`/education/exams/${data.id}/participants`, {
          computer_ids: examForm.computer_ids,
        });
      }
      setExamForm(emptyExamForm);
      setActiveTab(0);
      fetchExams();
    } catch { /* ignore */ }
    setSavingExam(false);
  };

  const handleSaveQuestion = async () => {
    setSavingQuestion(true);
    try {
      const payload: Record<string, unknown> = {
        question_type: questionForm.question_type,
        question_text: questionForm.question_text,
        points: questionForm.points,
        category: questionForm.category || undefined,
      };
      if (questionForm.question_type === "single" || questionForm.question_type === "multiple") {
        try { payload.options = JSON.parse(questionForm.options); } catch { payload.options = {}; }
      }
      if (questionForm.correct_answer) payload.correct_answer = questionForm.correct_answer;
      await api.post("/education/questions", payload);
      setShowQuestionModal(false);
      setQuestionForm(emptyQuestionForm);
      fetchQuestions();
    } catch { /* ignore */ }
    setSavingQuestion(false);
  };

  const handleBlockToggle = async (examId: string, computerId: string, block: boolean) => {
    try {
      await api.post(`/education/exams/${examId}/block-computer/${computerId}`, { block });
      fetchParticipants(examId);
    } catch { /* ignore */ }
  };

  const handleSendMessage = async () => {
    setSendingMessage(true);
    try {
      await api.post("/education/send-message", {
        computer_ids: messageComputers,
        message: messageText,
      });
      setMessageText("");
      setMessageComputers([]);
    } catch { /* ignore */ }
    setSendingMessage(false);
  };

  const handleSendTest = async () => {
    setSendingTest(true);
    try {
      await api.post("/education/send-test", {
        question_ids: testExamQuestions,
        computer_ids: testComputers,
      });
      setTestExamQuestions([]);
      setTestComputers([]);
    } catch { /* ignore */ }
    setSendingTest(false);
  };

  const toggleComputerSelection = (id: string) => {
    setExamForm((prev) => ({
      ...prev,
      computer_ids: prev.computer_ids.includes(id)
        ? prev.computer_ids.filter((c) => c !== id)
        : [...prev.computer_ids, id],
    }));
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Imtihonlar</h1>
        <div className="flex items-center gap-2 bg-white rounded-lg border border-slate-200 p-1">
          {tabs.map((tab, i) => (
            <button
              key={i}
              onClick={() => setActiveTab(i)}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === i ? "bg-indigo-600 text-white" : "text-slate-600 hover:text-slate-800"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 0 && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                  <th className="text-left px-4 py-3 font-medium">Nomi</th>
                  <th className="text-left px-4 py-3 font-medium">Fan</th>
                  <th className="text-center px-4 py-3 font-medium">Holat</th>
                  <th className="text-center px-4 py-3 font-medium">Davomiylik</th>
                  <th className="text-center px-4 py-3 font-medium">Bloklar</th>
                  <th className="text-center px-4 py-3 font-medium">Qatnashchilar</th>
                  <th className="text-right px-4 py-3 font-medium">Amallar</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {examsLoading ? (
                  <tr><td colSpan={7} className="text-center py-12 text-slate-400">Yuklanmoqda...</td></tr>
                ) : exams.length === 0 ? (
                  <tr><td colSpan={7} className="text-center py-12 text-slate-400">Imtihon topilmadi</td></tr>
                ) : (
                  exams.map((exam) => (
                    <tr key={exam.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-800">{exam.name}</td>
                      <td className="px-4 py-3 text-slate-600">{exam.subject || "—"}</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[exam.status]}`}>
                          {exam.status === "active" ? <Play size={12} /> : exam.status === "completed" ? <CheckCircle size={12} /> : exam.status === "cancelled" ? <XCircle size={12} /> : null}
                          {STATUS_LABELS[exam.status]}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center text-slate-600">{exam.duration_minutes} daqiqa</td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          {exam.block_internet && <Globe size={14} className="text-rose-500" title="Internet bloklangan" />}
                          {exam.block_usb && <Monitor size={14} className="text-rose-500" title="USB bloklangan" />}
                          {exam.block_alt_tab && <Terminal size={14} className="text-rose-500" title="Alt+Tab bloklangan" />}
                          {exam.block_task_manager && <Mouse size={14} className="text-rose-500" title="Task Manager bloklangan" />}
                          {exam.block_cmd && <Terminal size={14} className="text-rose-500" title="CMD bloklangan" />}
                          {!exam.block_internet && !exam.block_usb && !exam.block_alt_tab && !exam.block_task_manager && !exam.block_cmd && "—"}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center text-slate-600">{exam.participants_count ?? "—"}</td>
                      <td className="px-4 py-3 text-right">
                        {exam.status === "scheduled" && (
                          <button
                            onClick={() => handleExamAction(exam.id, "start")}
                            disabled={examActionLoading === `${exam.id}-start`}
                            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors disabled:opacity-50"
                          >
                            <Play size={12} /> Start
                          </button>
                        )}
                        {exam.status === "active" && (
                          <>
                            <button
                              onClick={() => { setMonitorExamId(exam.id); fetchParticipants(exam.id); setActiveTab(3); }}
                              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors mr-1"
                            >
                              <Users size={12} /> Monitor
                            </button>
                            <button
                              onClick={() => handleExamAction(exam.id, "stop")}
                              disabled={examActionLoading === `${exam.id}-stop`}
                              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-rose-50 text-rose-600 rounded-lg hover:bg-rose-100 transition-colors disabled:opacity-50"
                            >
                              <Square size={12} /> Stop
                            </button>
                          </>
                        )}
                        {(exam.status === "completed" || exam.status === "cancelled") && (
                          <button
                            onClick={() => handleDeleteExam(exam.id)}
                            className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg"
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 1 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="font-semibold text-slate-800 mb-4">Yangi imtihon yaratish</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Nomi</label>
              <input type="text" value={examForm.name} onChange={(e) => setExamForm({ ...examForm, name: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Fan</label>
              <input type="text" value={examForm.subject} onChange={(e) => setExamForm({ ...examForm, subject: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-slate-500 mb-1">Tavsif</label>
              <textarea value={examForm.description} onChange={(e) => setExamForm({ ...examForm, description: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" rows={2} />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Davomiylik (daqiqa)</label>
              <input type="number" value={examForm.duration_minutes} onChange={(e) => setExamForm({ ...examForm, duration_minutes: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" min={1} />
            </div>
          </div>

          <div className="mb-4">
            <h3 className="text-sm font-semibold text-slate-700 mb-2">Bloklash qoidalari</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {[
                { key: "block_internet", label: "Internet", icon: Globe },
                { key: "block_usb", label: "USB", icon: Monitor },
                { key: "block_alt_tab", label: "Alt+Tab", icon: Terminal },
                { key: "block_task_manager", label: "Task Manager", icon: Mouse },
                { key: "block_cmd", label: "CMD", icon: Terminal },
              ].map(({ key, label, icon: Icon }) => (
                <label key={key} className="flex items-center gap-2 cursor-pointer p-3 border border-slate-200 rounded-lg hover:border-indigo-300 transition-colors">
                  <input type="checkbox"
                    checked={(examForm as Record<string, boolean>)[key]}
                    onChange={(e) => setExamForm({ ...examForm, [key]: e.target.checked })}
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                  <Icon size={16} className="text-slate-500" />
                  <span className="text-sm text-slate-600">{label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            <label className="flex items-center gap-2 cursor-pointer p-3 border border-slate-200 rounded-lg hover:border-indigo-300 transition-colors">
              <input type="checkbox" checked={examForm.monitor_screens}
                onChange={(e) => setExamForm({ ...examForm, monitor_screens: e.target.checked })}
                className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
              <Shield size={16} className="text-slate-500" />
              <span className="text-sm text-slate-600">Ekranlarni kuzatish</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer p-3 border border-slate-200 rounded-lg hover:border-indigo-300 transition-colors">
              <input type="checkbox" checked={examForm.auto_submit_on_leave}
                onChange={(e) => setExamForm({ ...examForm, auto_submit_on_leave: e.target.checked })}
                className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
              <AlertTriangle size={16} className="text-slate-500" />
              <span className="text-sm text-slate-600">Chiqib ketganda avtomatik topshirish</span>
            </label>
          </div>

          <div className="mb-4">
            <h3 className="text-sm font-semibold text-slate-700 mb-2">Kompyuterlarni tanlash</h3>
            {computers.length === 0 ? (
              <p className="text-sm text-slate-400">Kompyuter topilmadi</p>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-48 overflow-y-auto p-2 border border-slate-200 rounded-lg">
                {computers.map((c) => (
                  <label key={c.id} className={`flex items-center gap-2 cursor-pointer p-2 rounded-lg text-sm transition-colors ${
                    examForm.computer_ids.includes(c.id) ? "bg-indigo-50 border border-indigo-300" : "border border-transparent hover:bg-slate-50"
                  }`}>
                    <input type="checkbox"
                      checked={examForm.computer_ids.includes(c.id)}
                      onChange={() => toggleComputerSelection(c.id)}
                      className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                    <span className="text-slate-700 truncate">{c.name}</span>
                  </label>
                ))}
              </div>
            )}
            <p className="text-xs text-slate-400 mt-1">{examForm.computer_ids.length} ta kompyuter tanlandi</p>
          </div>

          <button onClick={handleSaveExam} disabled={savingExam || !examForm.name}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
            <Plus size={16} /> {savingExam ? "Saqlanmoqda..." : "Imtihonni saqlash"}
          </button>
        </div>
      )}

      {activeTab === 2 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-800">Test savollari</h2>
            <button onClick={() => { setQuestionForm(emptyQuestionForm); setShowQuestionModal(true); }}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
              <Plus size={16} /> Yangi savol
            </button>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                    <th className="text-left px-4 py-3 font-medium">Turi</th>
                    <th className="text-left px-4 py-3 font-medium">Savol</th>
                    <th className="text-center px-4 py-3 font-medium">Ball</th>
                    <th className="text-left px-4 py-3 font-medium">Kategoriya</th>
                    <th className="text-right px-4 py-3 font-medium">Amallar</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {questionsLoading ? (
                    <tr><td colSpan={5} className="text-center py-12 text-slate-400">Yuklanmoqda...</td></tr>
                  ) : questions.length === 0 ? (
                    <tr><td colSpan={5} className="text-center py-12 text-slate-400">Savol topilmadi</td></tr>
                  ) : (
                    questions.map((q) => (
                      <tr key={q.id} className="hover:bg-slate-50">
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-600">
                            {QUESTION_TYPE_LABELS[q.question_type] || q.question_type}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-800 max-w-md truncate">{q.question_text}</td>
                        <td className="px-4 py-3 text-center font-medium text-slate-700">{q.points}</td>
                        <td className="px-4 py-3 text-slate-600">{q.category || "—"}</td>
                        <td className="px-4 py-3 text-right">
                          <button className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg">
                            <Pencil size={14} />
                          </button>
                          <button className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg ml-1">
                            <Trash2 size={14} />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 3 && (
        <div className="space-y-6">
          {monitorExamId && (
            <div className="flex items-center justify-between bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-center gap-3">
                <BookOpen size={20} className="text-indigo-600" />
                <div>
                  <h2 className="font-semibold text-slate-800">Jonli monitoring</h2>
                  <p className="text-xs text-slate-400">Imtihon ID: {monitorExamId}</p>
                </div>
              </div>
              <button onClick={() => setMonitorExamId("")} className="text-sm text-slate-400 hover:text-slate-600">Yopish</button>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-700">Qatnashchilar</h3>
                  <button onClick={() => monitorExamId && fetchParticipants(monitorExamId)}
                    className="text-xs text-indigo-600 hover:text-indigo-700">Yangilash</button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                        <th className="text-left px-4 py-3 font-medium">Talaba</th>
                        <th className="text-left px-4 py-3 font-medium">Kompyuter</th>
                        <th className="text-center px-4 py-3 font-medium">Holat</th>
                        <th className="text-center px-4 py-3 font-medium">Qoidabuzarlik</th>
                        <th className="text-center px-4 py-3 font-medium">Blok</th>
                        <th className="text-right px-4 py-3 font-medium">Amallar</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {participants.length === 0 ? (
                        <tr><td colSpan={6} className="text-center py-8 text-slate-400">Qatnashchi topilmadi</td></tr>
                      ) : (
                        participants.map((p) => (
                          <tr key={p.id} className="hover:bg-slate-50">
                            <td className="px-4 py-3 font-medium text-slate-800">{p.student_name}</td>
                            <td className="px-4 py-3 text-slate-600">{p.computer_name}</td>
                            <td className="px-4 py-3 text-center">
                              <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                                p.status === "active" ? "bg-emerald-100 text-emerald-700" :
                                p.status === "completed" ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-500"
                              }`}>
                                {p.status === "active" ? <Play size={10} /> : p.status === "completed" ? <CheckCircle size={10} /> : null}
                                {p.status}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              {p.violations > 0 ? (
                                <span className="inline-flex items-center gap-1 text-rose-600 font-medium">
                                  <AlertTriangle size={12} /> {p.violations}
                                </span>
                              ) : (
                                <span className="text-slate-400">0</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-center">
                              {p.is_blocked ? (
                                <span className="text-rose-600 text-xs font-medium">Bloklangan</span>
                              ) : (
                                <span className="text-emerald-600 text-xs font-medium">Ochiq</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-right">
                              <button
                                onClick={() => handleBlockToggle(monitorExamId, p.computer_id, !p.is_blocked)}
                                className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                                  p.is_blocked
                                    ? "bg-emerald-50 text-emerald-600 hover:bg-emerald-100"
                                    : "bg-rose-50 text-rose-600 hover:bg-rose-100"
                                }`}
                              >
                                <Shield size={12} /> {p.is_blocked ? "Blokni ochish" : "Bloklash"}
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-slate-200 p-4">
                <h3 className="text-sm font-semibold text-slate-700 mb-3">Xabar yuborish</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Kompyuterlar</label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 max-h-32 overflow-y-auto p-2 border border-slate-200 rounded-lg">
                      {participants.map((p) => (
                        <label key={p.id} className="flex items-center gap-2 cursor-pointer text-sm">
                          <input type="checkbox"
                            checked={messageComputers.includes(p.computer_id)}
                            onChange={() => setMessageComputers((prev) =>
                              prev.includes(p.computer_id) ? prev.filter((c) => c !== p.computer_id) : [...prev, p.computer_id]
                            )}
                            className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                          <span className="text-slate-700 truncate">{p.computer_name}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Xabar matni</label>
                    <textarea value={messageText} onChange={(e) => setMessageText(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" rows={2} />
                  </div>
                  <button onClick={handleSendMessage} disabled={sendingMessage || !messageText || messageComputers.length === 0}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
                    <Send size={14} /> {sendingMessage ? "Yuborilmoqda..." : "Yuborish"}
                  </button>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-slate-200 p-4">
                <h3 className="text-sm font-semibold text-slate-700 mb-3">Test yuborish</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Savollar</label>
                    <div className="grid grid-cols-1 gap-2 max-h-32 overflow-y-auto p-2 border border-slate-200 rounded-lg">
                      {questions.map((q) => (
                        <label key={q.id} className="flex items-center gap-2 cursor-pointer text-sm">
                          <input type="checkbox"
                            checked={testExamQuestions.includes(q.id)}
                            onChange={() => setTestExamQuestions((prev) =>
                              prev.includes(q.id) ? prev.filter((id) => id !== q.id) : [...prev, q.id]
                            )}
                            className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                          <span className="text-slate-700 truncate">{q.question_text}</span>
                          <span className="text-xs text-slate-400 ml-auto">({q.points} ball)</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Kompyuterlar</label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 max-h-32 overflow-y-auto p-2 border border-slate-200 rounded-lg">
                      {participants.map((p) => (
                        <label key={p.id} className="flex items-center gap-2 cursor-pointer text-sm">
                          <input type="checkbox"
                            checked={testComputers.includes(p.computer_id)}
                            onChange={() => setTestComputers((prev) =>
                              prev.includes(p.computer_id) ? prev.filter((c) => c !== p.computer_id) : [...prev, p.computer_id]
                            )}
                            className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                          <span className="text-slate-700 truncate">{p.computer_name}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  <button onClick={handleSendTest} disabled={sendingTest || testExamQuestions.length === 0 || testComputers.length === 0}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
                    <MessageSquare size={14} /> {sendingTest ? "Yuborilmoqda..." : "Testni yuborish"}
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">Faoliyat logi</h3>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {activityLogs.length === 0 ? (
                  <p className="text-sm text-slate-400 text-center py-4">Hech qanday faoliyat yo'q</p>
                ) : (
                  activityLogs.map((log) => (
                    <div key={log.id} className="flex items-start gap-3 p-2 rounded-lg bg-slate-50">
                      <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <AlertTriangle size={12} className="text-indigo-600" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs text-slate-700">{log.event}</p>
                        <p className="text-[10px] text-slate-400 mt-0.5">
                          {log.computer_name && `${log.computer_name}`}
                          {log.student_name && ` • ${log.student_name}`}
                          {` • ${new Date(log.created_at).toLocaleString("uz-UZ")}`}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {showQuestionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowQuestionModal(false)}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">Yangi savol</h2>
              <button onClick={() => setShowQuestionModal(false)} className="p-1 text-slate-400 hover:text-slate-600"><span className="text-lg">&times;</span></button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Turi</label>
                <select value={questionForm.question_type} onChange={(e) => setQuestionForm({ ...questionForm, question_type: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="single">Bir tanlov</option>
                  <option value="multiple">Ko'p tanlov</option>
                  <option value="text">Matn</option>
                  <option value="true_false">To'g'ri/Noto'g'ri</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Savol matni</label>
                <textarea value={questionForm.question_text} onChange={(e) => setQuestionForm({ ...questionForm, question_text: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" rows={3} />
              </div>
              {(questionForm.question_type === "single" || questionForm.question_type === "multiple") && (
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Variantlar (JSON)</label>
                  <textarea value={questionForm.options} onChange={(e) => setQuestionForm({ ...questionForm, options: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500" rows={3} />
                  <p className="text-[10px] text-slate-400 mt-1">Misol: {`{"A": "Variant 1", "B": "Variant 2", "C": "Variant 3", "D": "Variant 4"}`}</p>
                </div>
              )}
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">To'g'ri javob</label>
                <input type="text" value={questionForm.correct_answer} onChange={(e) => setQuestionForm({ ...questionForm, correct_answer: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Ball</label>
                  <input type="number" value={questionForm.points} onChange={(e) => setQuestionForm({ ...questionForm, points: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" min={0} />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Kategoriya</label>
                  <input type="text" value={questionForm.category} onChange={(e) => setQuestionForm({ ...questionForm, category: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
              <button onClick={() => setShowQuestionModal(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Bekor qilish</button>
              <button onClick={handleSaveQuestion} disabled={savingQuestion || !questionForm.question_text}
                className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
                {savingQuestion ? "Saqlanmoqda..." : "Saqlash"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
