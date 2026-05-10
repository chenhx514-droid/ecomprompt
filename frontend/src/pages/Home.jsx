import { useState, useEffect, useCallback } from 'react';
import { fetchPrompts } from '../api';
import PromptCard from '../components/PromptCard';
import SearchBar from '../components/SearchBar';
import CategoryTags from '../components/CategoryTags';

export default function Home() {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('trend_score');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchPrompts({ category, search, sort, page, page_size: 24 });
      setPrompts(page === 1 ? data.items : [...prompts, ...data.items]);
      setTotal(data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [category, search, sort, page]);

  useEffect(() => { load(); }, [load]);

  return (
    <div>
      <div className="mb-6 space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-lg font-bold">热门提示词</h1>
          <span className="text-xs text-gray-500">每3小时更新</span>
        </div>
        <SearchBar onSearch={(q) => { setSearch(q); setPage(1); }} />
        <div className="flex justify-between items-center">
          <CategoryTags selected={category} onSelect={(c) => { setCategory(c); setPage(1); }} />
          <div className="flex gap-1">
            {[
              { key: 'trend_score', label: '热度' },
              { key: 'usage_count', label: '使用' },
              { key: 'updated_at', label: '最新' },
            ].map(({ key, label }) => (
              <button key={key} onClick={() => { setSort(key); setPage(1); }}
                className={`px-2 py-1 text-xs rounded ${sort === key ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'}`}>
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && page === 1 ? (
        <div className="text-center py-20 text-gray-500">加载中...</div>
      ) : prompts.length === 0 ? (
        <div className="text-center py-20 text-gray-500">暂无提示词，请尝试其他筛选条件</div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {prompts.map((p) => <PromptCard key={p.id} prompt={p} />)}
          </div>
          {prompts.length < total && (
            <div className="text-center mt-8">
              <button onClick={() => setPage(page + 1)}
                className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition">
                加载更多 ({total - prompts.length} 条)
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
