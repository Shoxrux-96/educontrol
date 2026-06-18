import { useState } from "react";
import { Info, Plus } from "lucide-react";

export default function MessagesPage() {
  const [showForm, setShowForm] = useState(false);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Xabarlar</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700"
        >
          <Plus size={16} /> Yangi xabar
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
          <h2 className="font-semibold text-slate-800 mb-4">Yangi xabar yuborish</h2>
          <form className="space-y-4">
            <div>
              <label className="text-sm text-slate-600 block mb-1">Sarlavha</label>
              <input type="text" className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="Xabar sarlavhasi" />
            </div>
            <div>
              <label className="text-sm text-slate-600 block mb-1">Matn</label>
              <textarea rows={4} className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="Xabar matni" />
            </div>
            <div>
              <label className="text-sm text-slate-600 block mb-1">Qabul qiluvchi</label>
              <select className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="all">Barcha kompyuterlar</option>
                <option value="online">Online kompyuterlar</option>
              </select>
            </div>
            <button type="submit" className="px-6 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
              Yuborish
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-400">
        <Info size={40} className="mx-auto mb-3 text-slate-300" />
        <p>Xabarlar kompyuterlarga yuborilgandan so'ng bu yerda ko'rinadi</p>
      </div>
    </div>
  );
}
