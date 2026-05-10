import { useState, useEffect } from 'react';
import { fetchHotCategories, fetchHotKeywords, fetchTrendCalendar } from '../api';
import TrendChart from '../components/TrendChart';

export default function Trends() {
  const [categories, setCategories] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [calendar, setCalendar] = useState(null);

  useEffect(() => {
    fetchHotCategories().then(setCategories);
    fetchHotKeywords().then(setKeywords);
    fetchTrendCalendar().then(setCalendar);
  }, []);

  const now = new Date();
  const upcomingFestivals = (calendar?.festivals || []).filter((f) => {
    const d = new Date(now.getFullYear(), f.month - 1, f.day);
    return d >= now;
  }).slice(0, 4);

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-lg font-bold mb-6">趋势面板</h1>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-gray-900 rounded-xl p-4">
          <h2 className="text-sm font-medium text-gray-400 mb-3">品类热度榜</h2>
          <TrendChart data={categories.map((c) => ({ category: c.category, avg_score: c.avg_score }))} />
        </div>
        <div className="bg-gray-900 rounded-xl p-4">
          <h2 className="text-sm font-medium text-gray-400 mb-3">热搜关键词</h2>
          <div className="flex flex-wrap gap-2">
            {keywords.map((k) => (
              <span key={k.keyword} className="px-3 py-1.5 rounded-full text-xs"
                style={{ background: `rgba(99,102,241,${Math.min(1, k.heat / 100)})`, color: k.heat > 60 ? '#fff' : '#999' }}>
                {k.keyword} <span className="opacity-60">{Math.round(k.heat)}</span>
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-gray-900 rounded-xl p-4">
          <h2 className="text-sm font-medium text-gray-400 mb-3">即将到来的营销节点</h2>
          {upcomingFestivals.map((f) => {
            const d = new Date(now.getFullYear(), f.month - 1, f.day);
            const daysUntil = Math.ceil((d - now) / (1000 * 60 * 60 * 24));
            return (
              <div key={f.name} className="flex justify-between items-center py-2 border-b border-gray-800 last:border-0">
                <div><span className="text-sm font-medium">{f.name}</span>
                  <span className="text-xs text-gray-500 ml-2">{f.categories.slice(0, 2).join(' / ')}</span></div>
                <span className="text-xs text-amber-400">倒计时 {daysUntil} 天</span>
              </div>
            );
          })}
        </div>

        <div className="bg-gray-900 rounded-xl p-4">
          <h2 className="text-sm font-medium text-gray-400 mb-3">季节品类提醒</h2>
          {calendar?.seasonal?.filter((s) => s.months.includes(now.getMonth() + 1)).map((s) => (
            <div key={s.season} className="py-2">
              <span className="text-sm font-medium">{s.season}季活跃品类</span>
              <div className="flex gap-1 mt-1 flex-wrap">
                {s.boost_categories.map((bc) => (
                  <span key={bc} className="text-[10px] px-1.5 py-0.5 bg-gray-800 rounded text-gray-400">{bc}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
