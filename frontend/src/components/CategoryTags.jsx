const ALL_CATEGORIES = ['全部', '服饰', '美妆', '3C数码', '食品', '家居', '母婴', '运动户外'];

export default function CategoryTags({ selected, onSelect }) {
  return (
    <div className="flex gap-2 flex-wrap">
      {ALL_CATEGORIES.map((cat) => (
        <button
          key={cat}
          onClick={() => onSelect(cat === '全部' ? '' : cat)}
          className={`px-3 py-1 rounded-full text-xs font-medium transition ${
            (cat === '全部' && !selected) || selected === cat
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
