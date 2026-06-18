import { Link } from "react-router-dom";
import { Monitor, Shield, Gauge, Wifi, Mail, Phone, MapPin, ChevronRight, Globe, Users, Bell, BarChart3, Terminal, MessageSquare, Clock } from "lucide-react";

const features = [
  {
    icon: Monitor,
    title: "Kompyuterlarni masofaviy boshqarish",
    desc: "Barcha kompyuterlarni markazlashtirilgan holda kuzatish va boshqarish. Real vaqt rejimida holatini bilish.",
  },
  {
    icon: Shield,
    title: "Xavfsizlik siyosatlari",
    desc: "Internet, USB, dastur va prinskrinni bloklash siyosatlarini oson sozlash va kompyuterlarga tayinlash.",
  },
  {
    icon: Gauge,
    title: "Monitor va tahlil",
    desc: "CPU, RAM va disk bandligini real vaqt rejimida kuzatish. Ogohlantirish qoidalarini sozlash.",
  },
  {
    icon: Wifi,
    title: "Agent orqali ulanish",
    desc: "Har bir kompyuterga o'rnatilgan agent orqali tarmoq bo'ylab ishonchli va xavfsiz ulanish.",
  },
  {
    icon: Bell,
    title: "Avtomatik ogohlantirishlar",
    desc: "Belgilangan chegaralar oshib ketganda email va tizim orqali avtomatik xabardor qilish.",
  },
  {
    icon: BarChart3,
    title: "Hisobotlar va statistika",
    desc: "Kompyuter bandligi, foydalanuvchi faolligi va xatoliklar bo'yicha batafsil hisobotlar.",
  },
  {
    icon: Terminal,
    title: "Masofaviy buyruqlar",
    desc: "Kompyuterlarga masofadan buyruq yuborish, dastur o'rnatish va sozlamalarni o'zgartirish.",
  },
  {
    icon: MessageSquare,
    title: "Xabar yuborish",
    desc: "Barcha yoki tanlangan kompyuterlarga xabarlarni bir zumda yuborish imkoniyati.",
  },
];

const stats = [
  { value: "1000+", label: "Faol kompyuterlar" },
  { value: "50+", label: "Ta'lim muassasalari" },
  { value: "99.9%", label: "Ishonchlilik" },
  { value: "24/7", label: "Texnik yordam" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <Monitor className="w-6 h-6 text-indigo-600" />
              <span className="font-bold text-lg text-slate-800">EDU Control Pro</span>
            </div>
            <nav className="hidden md:flex items-center gap-8 text-sm">
              <a href="#features" className="text-slate-600 hover:text-indigo-600">Imkoniyatlar</a>
              <a href="#about" className="text-slate-600 hover:text-indigo-600">Nima uchun?</a>
              <a href="#pricing" className="text-slate-600 hover:text-indigo-600">Narxlar</a>
              <a href="#contact" className="text-slate-600 hover:text-indigo-600">Aloqa</a>
            </nav>
            <div className="flex items-center gap-3">
              <Link to="/login" className="px-4 py-2 text-sm text-slate-600 hover:text-indigo-600">
                Kirish
              </Link>
              <Link to="/login" className="px-5 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700">
                Bepul sinash
              </Link>
            </div>
          </div>
        </div>
      </header>

      <section className="bg-gradient-to-br from-indigo-900 via-blue-900 to-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl lg:text-6xl font-bold leading-tight mb-6">
              O'quv markazingizni <span className="text-indigo-400">aqlli boshqaring</span>
            </h1>
            <p className="text-lg lg:text-xl text-blue-200 mb-10 max-w-2xl mx-auto">
              EDU Control Pro — o'quv markazlaridagi barcha kompyuterlarni markazlashtirilgan holda boshqarish, 
              kuzatish va himoya qilish uchun zamonaviy platforma.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/login" className="w-full sm:w-auto px-8 py-3.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 flex items-center justify-center gap-2">
                Bepul boshlash <ChevronRight size={18} />
              </Link>
              <a href="#features" className="w-full sm:w-auto px-8 py-3.5 border border-white/20 text-white rounded-xl font-medium hover:bg-white/10 flex items-center justify-center">
                Ko'proq ma'lumot
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="py-12 bg-slate-50 border-y border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((s) => (
              <div key={s.label} className="text-center">
                <p className="text-3xl lg:text-4xl font-bold text-indigo-600">{s.value}</p>
                <p className="text-sm text-slate-500 mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-800 mb-4">Barcha imkoniyatlar</h2>
            <p className="text-slate-500 max-w-2xl mx-auto">
              O'quv markazingizni samarali boshqarish uchun kerakli barcha vositalar
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f) => (
              <div key={f.title} className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg hover:border-indigo-100 transition-all">
                <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-4">
                  <f.icon className="w-6 h-6 text-indigo-600" />
                </div>
                <h3 className="font-semibold text-slate-800 mb-2">{f.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="about" className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-slate-800 mb-6">
                Nima uchun EDU Control Pro?
              </h2>
              <div className="space-y-4">
                {[
                  { icon: Clock, title: "Vaqtni tejang", desc: "Har bir kompyuterga alohida borib sozlash o'rniga, barchasini markazdan boshqaring." },
                  { icon: Shield, title: "Xavfsizlikni oshiring", desc: "Internet, USB va boshqa qurilmalardan foydalanishni cheklash orqali ma'lumotlar xavfsizligini ta'minlang." },
                  { icon: Gauge, title: "Samaradorlikni kuzating", desc: "Kompyuterlarning bandligi va resurs sarfini real vaqt rejimida tahlil qiling." },
                  { icon: Bell, title: "Tezkor reaksiya", desc: "Nosozliklar va qoidabuzarliklar haqida darhol xabar oling va chora ko'ring." },
                ].map((item) => (
                  <div key={item.title} className="flex gap-4">
                    <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center shrink-0 mt-0.5">
                      <item.icon className="w-5 h-5 text-indigo-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-800">{item.title}</h3>
                      <p className="text-sm text-slate-500">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-gradient-to-br from-indigo-500 to-blue-600 rounded-2xl p-8 text-white">
              <Globe className="w-12 h-12 mb-4 text-indigo-200" />
              <h3 className="text-xl font-bold mb-3">100+ ta'lim muassasasi ishonchli hamkori</h3>
              <p className="text-blue-100 mb-6">
                O'zbekiston bo'ylab yuzdan ortiq o'quv markazlari va maktablar EDU Control Pro dan 
                foydalanib, kompyuter sinflarini samarali boshqarmoqda.
              </p>
              <div className="flex items-center gap-2 text-blue-200 text-sm">
                <Users className="w-5 h-5" />
                <span>5000+ o'quvchi himoyalangan kompyuterlarda tahsil olmoqda</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="pricing" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-800 mb-4">Narxlar</h2>
            <p className="text-slate-500 max-w-2xl mx-auto">
              Kichik o'quv markazidan tortib yirik ta'lim muassasasigacha mos tarif
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              {
                name: "Boshlang'ich",
                price: "0",
                desc: "Kichik sinflar uchun",
                features: ["10 tagacha kompyuter", "Asosiy monitoring", "Email orqali ogohlantirish", "Standart hisobotlar"],
                popular: false,
              },
              {
                name: "Professional",
                price: "49",
                desc: "O'rta va katta markazlar uchun",
                features: ["50 tagacha kompyuter", "To'liq monitoring", "Barcha turdagi siyosatlar", "Avtomatik hisobotlar", "Telegram bildirishnoma", "Masofaviy buyruqlar"],
                popular: true,
              },
              {
                name: "Korporativ",
                price: "99",
                desc: "Yirik muassasalar uchun",
                features: ["Cheksiz kompyuterlar", "Barcha imkoniyatlar", "Shaxsiy server", "24/7 texnik yordam", "Maxsus integratsiyalar", "Agent avtomatik yangilanish"],
                popular: false,
              },
            ].map((plan) => (
              <div key={plan.name} className={`rounded-xl border p-6 ${plan.popular ? "border-indigo-500 bg-indigo-50/50 ring-1 ring-indigo-500" : "border-slate-200 bg-white"}`}>
                {plan.popular && (
                  <span className="text-xs font-semibold text-indigo-600 bg-indigo-100 px-3 py-1 rounded-full">Eng ommabop</span>
                )}
                <h3 className="text-lg font-bold text-slate-800 mt-2">{plan.name}</h3>
                <p className="text-sm text-slate-500 mb-4">{plan.desc}</p>
                <p className="text-3xl font-bold text-slate-800 mb-6">
                  ${plan.price}<span className="text-sm font-normal text-slate-400">/oy</span>
                </p>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-slate-600">
                      <svg className="w-4 h-4 text-emerald-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link to="/login" className={`w-full block text-center py-2.5 rounded-lg text-sm font-medium ${plan.popular ? "bg-indigo-600 text-white hover:bg-indigo-700" : "border border-slate-200 text-slate-700 hover:bg-slate-50"}`}>
                  Boshlash
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="contact" className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12">
            <div>
              <h2 className="text-3xl font-bold text-slate-800 mb-4">Biz bilan bog'laning</h2>
              <p className="text-slate-500 mb-8">
                Savollaringiz bormi? Biz bilan bog'laning va mutaxassislarimiz sizga yordam beradi.
              </p>
              <div className="space-y-4">
                {[
                  { icon: Phone, text: "+998 (90) 123-45-67" },
                  { icon: Mail, text: "info@educontrol.uz" },
                  { icon: MapPin, text: "Toshkent sh., Chilonzor tumani, 9-mavze" },
                ].map((item) => (
                  <div key={item.text} className="flex items-center gap-3 text-slate-600">
                    <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center">
                      <item.icon className="w-5 h-5 text-indigo-600" />
                    </div>
                    <span>{item.text}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-800 mb-4">Xabar qoldirish</h3>
              <form className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-slate-600 block mb-1">Ism</label>
                    <input type="text" className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="Ismingiz" />
                  </div>
                  <div>
                    <label className="text-sm text-slate-600 block mb-1">Telefon</label>
                    <input type="tel" className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="+998" />
                  </div>
                </div>
                <div>
                  <label className="text-sm text-slate-600 block mb-1">Email</label>
                  <input type="email" className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="email@example.com" />
                </div>
                <div>
                  <label className="text-sm text-slate-600 block mb-1">Xabar</label>
                  <textarea rows={4} className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="Xabaringiz..." />
                </div>
                <button type="submit" className="w-full py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
                  Yuborish
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-slate-900 text-slate-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Monitor className="w-5 h-5 text-indigo-400" />
              <span className="font-semibold text-white">EDU Control Pro</span>
            </div>
            <p className="text-sm">&copy; {new Date().getFullYear()} EDU Control Pro. Barcha huquqlar himoyalangan.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
