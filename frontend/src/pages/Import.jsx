import { useState } from 'react';
import { importFile } from '../api';
import FileUpload from '../components/FileUpload';

export default function Import() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleUpload = async (file) => {
    setLoading(true); setError(''); setResult(null);
    try { const data = await importFile(file); setResult(data); }
    catch (e) { setError(e.response?.data?.detail || '导入失败，请检查文件格式'); }
    finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-lg font-bold mb-6">数据导入</h1>
      <FileUpload onUpload={handleUpload} />
      {loading && <div className="text-center py-10 text-gray-500">导入中...</div>}
      {error && <div className="mt-4 p-3 bg-red-900/30 border border-red-800 rounded-lg text-sm text-red-300">{error}</div>}
      {result && (
        <div className="mt-6 bg-gray-900 rounded-xl p-6">
          <h2 className="text-sm font-medium mb-3">导入成功</h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div><div className="text-2xl font-bold text-indigo-400">{result.imported}</div><div className="text-xs text-gray-500 mt-1">导入条数</div></div>
            <div><div className="text-2xl font-bold text-amber-400">{result.trends_extracted}</div><div className="text-xs text-gray-500 mt-1">提取品类</div></div>
            <div><div className="text-2xl font-bold text-emerald-400">{result.categories_found?.length || 0}</div><div className="text-xs text-gray-500 mt-1">趋势关键词</div></div>
          </div>
          {result.categories_found && result.categories_found.length > 0 && (
            <div className="mt-4 flex gap-1 flex-wrap">
              {result.categories_found.map((c) => <span key={c} className="text-xs px-2 py-1 bg-gray-800 rounded-full">{c}</span>)}
            </div>
          )}
        </div>
      )}
      <div className="mt-8 bg-gray-900 rounded-xl p-4">
        <h3 className="text-sm font-medium text-gray-400 mb-2">文件格式说明</h3>
        <div className="text-xs text-gray-500 space-y-1">
          <div><b>CSV格式：</b> 列名为 category/keyword/heat（或中文 品类/关键词/热度）</div>
          <div><b>JSON格式：</b> 数组，每个元素含 category/keyword/heat 字段</div>
        </div>
      </div>
    </div>
  );
}
