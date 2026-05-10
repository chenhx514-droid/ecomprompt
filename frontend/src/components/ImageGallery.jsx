import { useState } from 'react';

const PLACEHOLDER_IMG = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" fill="%23333"><rect width="600" height="400"/><text x="300" y="210" text-anchor="middle" fill="%23666" font-size="16">暂无预览图</text></svg>'
);

export default function ImageGallery({ images = [] }) {
  const [active, setActive] = useState(0);
  const imgs = images.length > 0 ? images : [PLACEHOLDER_IMG];

  return (
    <div>
      <div className="aspect-[3/2] bg-gray-900 rounded-lg overflow-hidden mb-2">
        <img src={imgs[active]} alt="" className="w-full h-full object-contain"
          onError={(e) => { e.target.src = PLACEHOLDER_IMG; }} />
      </div>
      {imgs.length > 1 && (
        <div className="flex gap-2 overflow-x-auto">
          {imgs.map((img, i) => (
            <button key={i} onClick={() => setActive(i)}
              className={`flex-shrink-0 w-16 h-16 rounded overflow-hidden border-2 transition ${
                i === active ? 'border-indigo-400' : 'border-transparent opacity-60 hover:opacity-100'
              }`}>
              <img src={img} alt="" className="w-full h-full object-cover" onError={(e) => { e.target.style.display = 'none'; }} />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
