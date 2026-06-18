import { BarChart3, Download } from "lucide-react";

const reports = [
  { id: 1, name: "Kompyuter holati", desc: "Barcha kompyuterlarning umumiy holati", color: "indigo" },
  { id: 2, name: "Siyosat bajarilishi", desc: "Siyosatlarning kompyuterlarda bajarilishi", color: "emerald" },
  { id: 3, name: "Foydalanuvchi faolligi", desc: "Foydalanuvchilarning tizimdagi faolligi", color: "amber" },
  { id: 4, name: "Xatoliklar tahlili", desc: "Tizimdagi xatoliklar statistikasi", color: "rose" },
  { id: 5, name: "Bandlik hisoboti", desc: "Kompyuterlarning bandlik vaqti tahlili", color: "violet" },
  { id: 6, name: "Audit xulosasi", desc: "Audit jurnali bo'yicha umumiy hisobot", color: "blue" },
];

const colorMap: Record<string, string> = {
  indigo: "bg-indigo-50 border-indigo-200 hover:bg-indigo-100",
  emerald: "bg-emerald-50 border-emerald-200 hover:bg-emerald-100",
  amber: "bg-amber-50 border-amber-200 hover:bg-amber-100",
  rose: "bg-rose-50 border-rose-200 hover:bg-rose-100",
  violet: "bg-violet-50 border-violet-200 hover:bg-violet-100",
  blue: "bg-blue-50 border-blue-200 hover:bg-blue-100",
};

export default function ReportsPage() {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Hisobotlar</h1>
        <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-sm hover:bg-slate-50">
          <Download size={16} /> Eksport
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reports.map((r) => (
          <button key={r.id} className={`text-left rounded-xl border p-5 transition-colors ${colorMap[r.color] || colorMap.blue}`}>
            <BarChart3 size={24} className="text-slate-600 mb-3" />
            <h3 className="font-semibold text-slate-800">{r.name}</h3>
            <p className="text-sm text-slate-500 mt-1">{r.desc}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
