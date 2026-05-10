import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchPrompt, usePrompt, enhancePrompt } from '../api';
import ImageGallery from '../components/ImageGallery';

export default function Detail() {
  const { id } = useParams();
  const [prompt, setPrompt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [enhancing, setEnhancing] = useState(false);

  useEffect(() => {
    fetchPrompt(id).then((data) => { setPrompt(data); setLoading(false); });
  }, [id]);

  const handleCopy = async () => {
    if (!prompt) return;
    await navigator.clipboard.writeText(prompt.content);
    setCopied(true);
    await usePrompt(prompt.id);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleEnhance = async () => {
    setEnhancing(true);
    try {
      const result = await enhancePrompt(prompt.id);
      setPrompt({ ...prompt, content: result.enhanced });
    } catch (e) { console.error(e); }
    finally { setEnhancing(false); }
  };

  if (loading) return <div className="text-center py-20 text-gray-500">加载中...</div>;
  if (!prompt) return <div className="text-center py-20 text-gray-500">未找到该提示词</div>;

  const images = typeof prompt.preview_images === 'string'
    ? JSON.parse(prompt.preview_images || '[]')
    : (prompt.preview_images || []);

  return (
    <div className="max-w-5xl mx-auto">
      <Link to="/" className="text-sm text-gray-400 hover:text-white mb-4 inline-block">← 返回列表</Link>
      <div className="grid md:grid-cols-2 gap-8 mt-2">
        <ImageGallery images={images} />
        <div>
          <h1 className="text-xl font-bold">{prompt.title}</h1>
          <div className="flex gap-2 mt-3 flex-wrap">
            <span className="text-xs px-2 py-1 bg-gray-800 rounded-full">{prompt.category}</span>
            <span className="text-xs px-2 py-1 bg-gray-800 rounded-full">{prompt.scenario}</span>
            <span className="text-xs px-2 py-1 bg-gray-800 rounded-full">{prompt.platform}</span>
            <span className="text-xs px-2 py-1 bg-gray-800 rounded-full">{prompt.output_type}</span>
          </div>
          <div className="mt-4 bg-gray-900 rounded-lg p-4 font-mono text-sm leading-relaxed whitespace-pre-wrap max-h-80 overflow-y-auto">
            {prompt.content}
          </div>
          <div className="flex gap-3 mt-4">
            <button onClick={handleCopy}
              className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium transition">
              {copied ? '已复制!' : '复制提示词'}
            </button>
            <button onClick={handleEnhance} disabled={enhancing}
              className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-medium transition disabled:opacity-50">
              {enhancing ? '优化中...' : 'AI优化'}
            </button>
          </div>
          <div className="mt-4 text-xs text-gray-500 space-y-1">
            <div>来源：{prompt.source} · 更新于 {prompt.updated_at}</div>
            <div>{prompt.usage_count} 次使用 · 热度 {prompt.trend_score}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
