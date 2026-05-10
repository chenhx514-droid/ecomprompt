import { Link } from 'react-router-dom';

const PLACEHOLDER_IMG = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" fill="%23333"><rect width="300" height="200"/><text x="150" y="105" text-anchor="middle" fill="%23666" font-size="14">暂无预览</text></svg>'
);

export default function PromptCard({ prompt }) {
  const images = typeof prompt.preview_images === 'string'
    ? JSON.parse(prompt.preview_images || '[]')
    : (prompt.preview_images || []);
  const imgSrc = images.length > 0 ? images[0] : PLACEHOLDER_IMG;

  return (
    <Link
      to={`/prompt/${prompt.id}`}
      className="block bg-gray-900 rounded-xl overflow-hidden border border-gray-800 hover:border-indigo-500 transition group"
    >
      <div className="aspect-[3/2] bg-gray-800 overflow-hidden">
        <img src={imgSrc} alt={prompt.title} className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
          onError={(e) => { e.target.src = PLACEHOLDER_IMG; }} />
      </div>
      <div className="p-3">
        <h3 className="font-semibold text-sm text-white truncate">{prompt.title}</h3>
        <div className="flex gap-1 mt-1.5 flex-wrap">
          <span className="text-[10px] px-1.5 py-0.5 bg-gray-800 rounded text-gray-400">{prompt.category}</span>
          <span className="text-[10px] px-1.5 py-0.5 bg-gray-800 rounded text-gray-400">{prompt.scenario}</span>
          <span className="text-[10px] px-1.5 py-0.5 bg-gray-800 rounded text-gray-400">{prompt.platform}</span>
        </div>
        <p className="text-xs text-gray-500 mt-2 line-clamp-2">{prompt.content}</p>
        <div className="flex justify-between items-center mt-3">
          <span className="text-xs text-amber-400 font-medium">
            {prompt.trend_score >= 80 ? '🔥' : '⭐'} {prompt.trend_score}
          </span>
          <span className="text-[10px] text-gray-600">{prompt.usage_count} 使用</span>
        </div>
      </div>
    </Link>
  );
}
