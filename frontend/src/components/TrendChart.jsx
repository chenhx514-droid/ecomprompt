import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function TrendChart({ data }) {
  if (!data || data.length === 0) return <div className="text-center py-10 text-gray-500">暂无趋势数据</div>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis dataKey="category" tick={{ fill: '#888', fontSize: 12 }} />
        <YAxis tick={{ fill: '#888', fontSize: 12 }} />
        <Tooltip contentStyle={{ background: '#1e1b4b', border: '1px solid #333', borderRadius: 8 }} labelStyle={{ color: '#fff' }} />
        <Bar dataKey="avg_score" fill="#6366f1" radius={[4, 4, 0, 0]} name="平均热度" />
      </BarChart>
    </ResponsiveContainer>
  );
}
