import { useState, useEffect, useCallback } from 'react';
import { fetchPrompts, fetchFolders } from '../api';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import PromptCard from '../components/PromptCard';
import SearchBar from '../components/SearchBar';
import CategoryTags from '../components/CategoryTags';

export default function Home() {
  const { user } = useAuth();
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [crawling, setCrawling] = useState(false);
  const [category, setCategory] = useState('');
  const [folder, setFolder] = useState('');
  const [folders, setFolders] = useState([]);
  const [showCollected, setShowCollected] = useState(false);

  const triggerCrawl = async () => {
    setCrawling(true);
    try { await axios.post('/api/crawl'); }
    catch(e) { console.error(e); }
    setTimeout(() => { setCrawling(false); window.location.reload(); }, 10000);
  };
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('trend_score');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { category, search, sort, page, page_size: 24 };
      if (showCollected) {
        params.source = 'user_collect';
        if (folder) params.folder = folder;
      }
      const data = await fetchPrompts(params);
      setPrompts(page === 1 ? data.items : [...prompts, ...data.items]);
      setTotal(data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [category, search, sort, page, showCollected, folder]);

  useEffect(() => { load(); }, [load]);

  const toggleCollected = () => {
    if (!showCollected) {
      fetchFolders().then(setFolders).catch(() => {});
    }
    setShowCollected(!showCollected);
    setFolder('');
    setCategory('');
    setPage(1);
  };

  return (
    <div>
      <div className="mb-6 space-y-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold">{showCollected ? '个人收录' : '热门提示词'}</h1>
            {user && (
              <button
                onClick={toggleCollected}
                className={`px-3 py-1 text-xs rounded-lg transition ${
                  showCollected
                    ? 'bg-amber-600 hover:bg-amber-500 text-white'
                    : 'bg-gray-800 hover:bg-gray-700 text-gray-400'
                }`}
              >
                {showCollected ? '查看全部' : '我的收录'}
              </button>
            )}
            {!showCollected && (
              <button
                onClick={triggerCrawl}
                disabled={crawling}
                className="px-3 py-1 text-xs bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 rounded-lg transition"
              >
                {crawling ? '抓取中...' : '抓取最新'}
              </button>
            )}
          </div>
          <span className="text-xs text-gray-500">每3小时更新</span>
        </div>
        {showCollected && folders.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            <button
              onClick={() => { setFolder(''); setPage(1); }}
              className={`px-2 py-1 text-xs rounded transition ${
                folder === '' ? 'bg-amber-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              全部
            </button>
            {folders.map((f) => (
              <button
                key={f}
                onClick={() => { setFolder(f); setPage(1); }}
                className={`px-2 py-1 text-xs rounded transition ${
                  folder === f ? 'bg-amber-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        )}
        <SearchBar onSearch={(q) => { setSearch(q); setPage(1); }} />
        <div className="flex justify-between items-center">
          {!showCollected ? (
            <CategoryTags selected={category} onSelect={(c) => { setCategory(c); setPage(1); }} />
          ) : (
            <div />
          )}
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
