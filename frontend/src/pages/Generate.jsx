import { useState } from 'react';
import { generatePrompt } from '../api';

const CATEGORIES = ['服饰', '美妆', '3C数码', '食品', '家居', '母婴', '运动户外', '珠宝饰品'];
const SCENARIOS = ['新品推广', '大促促销', '清仓甩卖', '日常种草', '测评推荐'];
const PLATFORMS = ['淘宝', '天猫', '拼多多', '小红书', '抖音', 'TikTok', 'Amazon'];
const OUTPUT_TYPES = ['主图提示词', '详情页文案', '标题优化', '短视频脚本', '广告投放文案'];

export default function Generate() {
  const [form, setForm] = useState({
    category: '服饰', scenario: '新品推广', platform: '小红书', output_type: '主图提示词', description: '',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setResult(null);
    try { const data = await generatePrompt(form); setResult(data); }
    catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleCopy = async () => {
    if (!result) return;
    await navigator.clipboard.writeText(result.prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const s = "w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500";

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-lg font-bold mb-6">AI 提示词生成</h1>
      <div className="grid md:grid-cols-2 gap-8">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="text-xs text-gray-400 block mb-1">产品品类</label>
            <select className={s} value={form.category} onChange={(e) => setForm({...form, category: e.target.value})}>
              {CATEGORIES.map((c) => <option key={c}>{c}</option>)}</select></div>
          <div><label className="text-xs text-gray-400 block mb-1">使用场景</label>
            <select className={s} value={form.scenario} onChange={(e) => setForm({...form, scenario: e.target.value})}>
              {SCENARIOS.map((v) => <option key={v}>{v}</option>)}</select></div>
          <div><label className="text-xs text-gray-400 block mb-1">目标平台</label>
            <select className={s} value={form.platform} onChange={(e) => setForm({...form, platform: e.target.value})}>
              {PLATFORMS.map((v) => <option key={v}>{v}</option>)}</select></div>
          <div><label className="text-xs text-gray-400 block mb-1">输出类型</label>
            <select className={s} value={form.output_type} onChange={(e) => setForm({...form, output_type: e.target.value})}>
              {OUTPUT_TYPES.map((v) => <option key={v}>{v}</option>)}</select></div>
          <div><label className="text-xs text-gray-400 block mb-1">补充描述（可选）</label>
            <textarea className={s} rows={3} value={form.description}
              onChange={(e) => setForm({...form, description: e.target.value})}
              placeholder="例如：轻薄雪纺面料，V领设计，适合25-35岁女性..." /></div>
          <button type="submit" disabled={loading}
            className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium transition disabled:opacity-50">
            {loading ? '生成中...' : '生成提示词'}</button>
        </form>

        <div>
          <h2 className="text-sm font-medium text-gray-400 mb-3">生成结果</h2>
          {loading && <div className="text-center py-20 text-gray-500">AI 正在生成...</div>}
          {!loading && !result && <div className="text-center py-20 text-gray-600 text-sm">选择参数后点击生成</div>}
          {result && (
            <div className="space-y-4">
              <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm leading-relaxed whitespace-pre-wrap max-h-80 overflow-y-auto">
                {result.prompt}</div>
              {result.explanation && <div className="bg-gray-900 rounded-lg p-3 text-xs text-gray-400">{result.explanation}</div>}
              <div className="flex gap-2">
                <button onClick={handleCopy} className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm transition">
                  {copied ? '已复制!' : '复制'}</button>
                <button onClick={handleSubmit} className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition">
                  重新生成</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
