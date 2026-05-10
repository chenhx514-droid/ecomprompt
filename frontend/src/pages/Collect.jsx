import { useState, useRef, useEffect } from 'react';
import { collectPrompt, fetchFolders } from '../api';

const CATEGORIES = ['服饰', '美妆', '3C数码', '食品', '家居', '母婴', '运动户外', '珠宝饰品', '其他'];
const SCENARIOS = ['日常种草', '促销大促', '新品首发', '节日营销', '品牌宣传'];
const PLATFORMS = ['通用', '淘宝', '天猫', '拼多多', '小红书', '抖音', '亚马逊', '速卖通'];
const OUTPUT_TYPES = ['主图提示词', '详情图提示词', '直播话术', '短视频脚本'];

export default function Collect() {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('其他');
  const [scenario, setScenario] = useState('日常种草');
  const [platform, setPlatform] = useState('通用');
  const [outputType, setOutputType] = useState('主图提示词');
  const [content, setContent] = useState('');
  const [folder, setFolder] = useState('默认');
  const [folders, setFolders] = useState(['默认']);
  const [newFolder, setNewFolder] = useState('');
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [images, setImages] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const fileRef = useRef(null);

  useEffect(() => {
    fetchFolders().then(setFolders).catch(() => {});
  }, [result]);

  const handleFiles = (e) => {
    const files = Array.from(e.target.files);
    setImages((prev) => [...prev, ...files]);
    files.forEach((f) => {
      const reader = new FileReader();
      reader.onload = (ev) => setPreviews((p) => [...p, ev.target.result]);
      reader.readAsDataURL(f);
    });
    e.target.value = '';
  };

  const removeImage = (i) => {
    setImages((prev) => prev.filter((_, idx) => idx !== i));
    setPreviews((prev) => prev.filter((_, idx) => idx !== i));
  };

  const addFolder = () => {
    const name = newFolder.trim();
    if (!name) return;
    if (folders.includes(name)) {
      setFolder(name);
    } else {
      setFolders((prev) => [...prev, name]);
      setFolder(name);
    }
    setNewFolder('');
    setShowNewFolder(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('请填写标题和提示词内容');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await collectPrompt({
        title: title.trim(),
        category,
        scenario,
        platform,
        output_type: outputType,
        content: content.trim(),
        folder,
        images,
      });
      setResult(data);
      setTitle('');
      setContent('');
      setImages([]);
      setPreviews([]);
    } catch (err) {
      setError(err.response?.data?.detail || '收录失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-lg font-bold mb-6">收录提示词</h1>

      {result ? (
        <div className="bg-emerald-900/30 border border-emerald-800 rounded-xl p-6 mb-6">
          <div className="text-2xl font-bold text-emerald-400">{result.message}</div>
          <div className="text-sm text-gray-400 mt-2">
            {result.images_saved > 0 && `已保存 ${result.images_saved} 张图片`}
          </div>
          <button
            onClick={() => setResult(null)}
            className="mt-4 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm transition"
          >
            继续收录
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="bg-gray-900 rounded-xl p-6 space-y-5">
          <div>
            <label className="block text-sm text-gray-400 mb-1.5">标题 *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="例如：夏日美妆产品主图"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">收藏文件夹</label>
              {showNewFolder ? (
                <div className="flex gap-1">
                  <input
                    type="text"
                    value={newFolder}
                    onChange={(e) => setNewFolder(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addFolder(); } }}
                    placeholder="输入文件夹名"
                    className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:border-indigo-500"
                    autoFocus
                  />
                  <button type="button" onClick={addFolder}
                    className="px-3 py-1.5 bg-indigo-600 rounded-lg text-xs hover:bg-indigo-500 transition">
                    确认
                  </button>
                  <button type="button" onClick={() => { setShowNewFolder(false); setNewFolder(''); }}
                    className="px-2 py-1.5 bg-gray-700 rounded-lg text-xs hover:bg-gray-600 transition">
                    取消
                  </button>
                </div>
              ) : (
                <div className="flex gap-1">
                  <select
                    value={folder}
                    onChange={(e) => setFolder(e.target.value)}
                    className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                  >
                    {folders.map((f) => (
                      <option key={f} value={f}>{f}</option>
                    ))}
                  </select>
                  <button type="button" onClick={() => setShowNewFolder(true)}
                    className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-xs transition whitespace-nowrap">
                    + 新建
                  </button>
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">品类</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">场景</label>
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                {SCENARIOS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">平台</label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                {PLATFORMS.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">输出类型</label>
              <select
                value={outputType}
                onChange={(e) => setOutputType(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                {OUTPUT_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1.5">提示词内容 *</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={6}
              placeholder="在此粘贴或编写提示词内容..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 resize-y"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1.5">
              上传图片（JPG/PNG/WebP/GIF，可选多张）
            </label>
            <input
              ref={fileRef}
              type="file"
              multiple
              accept=".jpg,.jpeg,.png,.webp,.gif"
              onChange={handleFiles}
              className="block w-full text-sm text-gray-400 file:mr-3 file:py-1.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:bg-gray-700 file:text-gray-200 hover:file:bg-gray-600"
            />
            {previews.length > 0 && (
              <div className="flex gap-2 mt-3 flex-wrap">
                {previews.map((url, i) => (
                  <div key={i} className="relative group">
                    <img src={url} alt="" className="w-20 h-20 object-cover rounded-lg border border-gray-700" />
                    <button
                      type="button"
                      onClick={() => removeImage(i)}
                      className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition"
                    >
                      x
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {error && (
            <div className="p-3 bg-red-900/30 border border-red-800 rounded-lg text-sm text-red-300">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-sm font-medium transition"
          >
            {loading ? '收录中...' : '提交收录'}
          </button>
        </form>
      )}
    </div>
  );
}
