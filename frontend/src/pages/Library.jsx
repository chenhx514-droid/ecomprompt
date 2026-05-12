import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { fetchPrompts, fetchFolders, fetchLibraryStats, deleteLibraryPrompt, moveLibraryPrompt } from '../api';
import CategoryTags from '../components/CategoryTags';
import SearchBar from '../components/SearchBar';

export default function Library() {
  const [prompts, setPrompts] = useState([]);
  const [folders, setFolders] = useState([]);
  const [stats, setStats] = useState(null);
  const [category, setCategory] = useState('');
  const [folder, setFolder] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showDeleteId, setShowDeleteId] = useState(null);
  const [showMoveId, setShowMoveId] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        source: 'user_collect',
        category,
        search,
        sort: 'date',
        page,
        page_size: 24,
      };
      if (folder) params.folder = folder;
      const data = await fetchPrompts(params);
      setPrompts(page === 1 ? data.items : [...prompts, ...data.items]);
      setTotal(data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [category, search, page, folder]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    fetchFolders().then(setFolders).catch(() => {});
    fetchLibraryStats().then(setStats).catch(() => {});
  }, []);

  const handleDelete = async (id) => {
    await deleteLibraryPrompt(id);
    setShowDeleteId(null);
    setPrompts(prompts.filter(p => p.id !== id));
    setTotal(t => t - 1);
  };

  const handleMove = async (id, newFolder) => {
    await moveLibraryPrompt(id, newFolder);
    setShowMoveId(null);
    load();
  };

  const handleCategoryChange = (cat) => {
    setCategory(cat);
    setPage(1);
    setPrompts([]);
  };

  const handleFolderChange = (f) => {
    setFolder(f);
    setPage(1);
    setPrompts([]);
  };

  const handleSearch = (q) => {
    setSearch(q);
    setPage(1);
    setPrompts([]);
  };

  const loadMore = () => setPage(p => p + 1);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-1">我的仓库</h1>
      <p className="text-gray-400 mb-6">管理你收藏的提示词和图片</p>

      {/* Stats Bar */}
      {stats && (
        <div className="flex flex-wrap gap-4 mb-6">
          <div className="bg-gray-900 rounded-xl border border-gray-800 px-5 py-3">
            <div className="text-2xl font-bold text-indigo-400">{stats.total}</div>
            <div className="text-xs text-gray-500">总收录</div>
          </div>
          {stats.categories?.slice(0, 4).map(c => (
            <div key={c.name} className="bg-gray-900 rounded-xl border border-gray-800 px-5 py-3">
              <div className="text-2xl font-bold text-amber-400">{c.count}</div>
              <div className="text-xs text-gray-500">{c.name}</div>
            </div>
          ))}
          <div className="bg-gray-900 rounded-xl border border-gray-800 px-5 py-3">
            <div className="text-2xl font-bold text-emerald-400">{stats.folders?.length || 0}</div>
            <div className="text-xs text-gray-500">文件夹</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
        <SearchBar onSearch={handleSearch} />

        {folders.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            <button
              onClick={() => handleFolderChange('')}
              className={`px-3 py-1.5 rounded text-sm transition ${
                !folder ? 'bg-amber-600 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-800'
              }`}
            >
              全部文件夹
            </button>
            {folders.map(f => (
              <button
                key={f}
                onClick={() => handleFolderChange(f)}
                className={`px-3 py-1.5 rounded text-sm transition ${
                  folder === f ? 'bg-amber-600 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        )}
      </div>

      <CategoryTags onSelect={handleCategoryChange} selected={category} />

      {/* Prompt Grid */}
      {loading && prompts.length === 0 ? (
        <div className="text-center py-20 text-gray-500">加载中...</div>
      ) : prompts.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-4xl mb-4">📦</div>
          <p className="text-gray-400 text-lg mb-2">仓库还是空的</p>
          <p className="text-gray-500 text-sm mb-4">去收录页面添加你的第一条提示词</p>
          <Link
            to="/collect"
            className="inline-block px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition"
          >
            去收录
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {prompts.map(prompt => (
              <div
                key={prompt.id}
                className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden group hover:border-gray-700 transition"
              >
                {/* Image */}
                <Link to={`/prompt/${prompt.id}`} className="block aspect-square bg-gray-800 overflow-hidden">
                  {prompt.preview_images?.length > 0 ? (
                    <img
                      src={prompt.preview_images[0]}
                      alt={prompt.title}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-600 text-4xl">
                      📷
                    </div>
                  )}
                </Link>

                {/* Info */}
                <div className="p-3">
                  <Link
                    to={`/prompt/${prompt.id}`}
                    className="text-sm font-medium text-white line-clamp-2 hover:text-indigo-400 transition"
                  >
                    {prompt.title}
                  </Link>

                  <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                    {prompt.category && prompt.category !== '其他' && (
                      <span className="px-1.5 py-0.5 bg-indigo-900/50 text-indigo-300 text-xs rounded">
                        {prompt.category}
                      </span>
                    )}
                    <span className="px-1.5 py-0.5 bg-gray-800 text-gray-400 text-xs rounded">
                      {prompt.collection_folder || '默认'}
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-800">
                    {/* Move */}
                    <button
                      onClick={() => setShowMoveId(showMoveId === prompt.id ? null : prompt.id)}
                      className="text-xs text-gray-500 hover:text-white transition"
                    >
                      {showMoveId === prompt.id ? '取消' : '移动'}
                    </button>
                    {/* Delete */}
                    <button
                      onClick={() => setShowDeleteId(showDeleteId === prompt.id ? null : prompt.id)}
                      className="text-xs text-gray-500 hover:text-red-400 transition"
                    >
                      {showDeleteId === prompt.id ? '取消' : '删除'}
                    </button>
                  </div>

                  {/* Move Panel */}
                  {showMoveId === prompt.id && (
                    <div className="mt-2 pt-2 border-t border-gray-800">
                      <div className="text-xs text-gray-500 mb-1.5">移动到：</div>
                      <div className="flex gap-1 flex-wrap">
                        {folders.map(f => (
                          <button
                            key={f}
                            onClick={() => handleMove(prompt.id, f)}
                            className={`px-2 py-1 text-xs rounded transition ${
                              prompt.collection_folder === f
                                ? 'bg-amber-600 text-white'
                                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                            }`}
                          >
                            {f}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Delete Confirm */}
                  {showDeleteId === prompt.id && (
                    <div className="mt-2 pt-2 border-t border-gray-800">
                      <p className="text-xs text-red-400 mb-2">确定要删除吗？不可恢复</p>
                      <button
                        onClick={() => handleDelete(prompt.id)}
                        className="px-3 py-1 bg-red-600 hover:bg-red-500 text-white text-xs rounded transition"
                      >
                        确认删除
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Load More */}
          {prompts.length < total && (
            <div className="text-center mt-8">
              <button
                onClick={loadMore}
                disabled={loading}
                className="px-6 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition disabled:opacity-50"
              >
                {loading ? '加载中...' : `加载更多 (${total - prompts.length} 条剩余)`}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
