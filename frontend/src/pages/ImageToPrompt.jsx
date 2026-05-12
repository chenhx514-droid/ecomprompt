import { useState, useRef } from 'react';
import axios from 'axios';

function compressImage(file) {
  return new Promise((resolve, reject) => {
    const MAX_SIZE = 1024;
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        let { width, height } = img;
        if (width <= MAX_SIZE && height <= MAX_SIZE) {
          resolve(file);
          return;
        }
        if (width > height) { height = Math.round(height * MAX_SIZE / width); width = MAX_SIZE; }
        else { width = Math.round(width * MAX_SIZE / height); height = MAX_SIZE; }
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        canvas.toBlob((blob) => {
          resolve(new File([blob], file.name, { type: 'image/jpeg' }));
        }, 'image/jpeg', 0.85);
      };
      img.src = reader.result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

const FORMats = [
  { key: 'general', label: '通用提示词', icon: '✦' },
  { key: 'midjourney', label: 'Midjourney', icon: '🎨' },
  { key: 'sd', label: 'Stable Diffusion', icon: '🖼' },
  { key: 'flux', label: 'Flux', icon: '🌊' },
];

export default function ImageToPrompt() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [format, setFormat] = useState('general');
  const [copied, setCopied] = useState(false);
  const fileRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setError('请上传图片文件 (JPEG/PNG/WebP/GIF)');
      return;
    }
    if (file.size > 4 * 1024 * 1024) {
      setError('图片大小不能超过 4MB');
      return;
    }
    setError('');
    setResult(null);
    setImage(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = async () => {
    if (!image) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const compressed = await compressImage(image);
      const form = new FormData();
      form.append('image', compressed);
      form.append('model_format', format);

      const { data } = await axios.post('/api/image-to-prompt', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
      });
      setResult(data);
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('请求超时，图片可能太大，请尝试较小的图片（建议小于 1MB）');
      } else {
        const msg = err.response?.data?.detail || err.message;
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const copyText = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const displayPrompt = result?.prompts?.[format] || result?.prompt || '';

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-white mb-2">图片反推提示词</h1>
      <p className="text-gray-400 mb-8">上传一张图片，AI 自动分析并生成可用于 AI 绘图工具的提示词</p>

      {/* Upload Zone */}
      <div
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all mb-6
          ${preview ? 'border-indigo-500/50 bg-indigo-500/5' : 'border-gray-600 hover:border-indigo-400 bg-gray-900'}`}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
      >
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />

        {preview ? (
          <div className="flex flex-col items-center gap-4">
            <img
              src={preview}
              alt="Preview"
              className="max-h-64 rounded-lg object-contain"
            />
            <span className="text-gray-400 text-sm">点击重新选择图片</span>
          </div>
        ) : (
          <div className="py-8">
            <div className="text-4xl mb-3">📤</div>
            <p className="text-gray-300 text-lg mb-1">拖拽图片到此处，或点击上传</p>
            <p className="text-gray-500 text-sm">支持 JPG, PNG, WebP, GIF — 最大 4MB</p>
          </div>
        )}
      </div>

      {/* Model Format Selector */}
      <div className="flex flex-wrap gap-2 mb-6">
        {FORMats.map((f) => (
          <button
            key={f.key}
            onClick={() => setFormat(f.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all
              ${format === f.key
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'}`}
          >
            {f.icon} {f.label}
          </button>
        ))}
      </div>

      {/* Analyze Button */}
      <button
        onClick={handleSubmit}
        disabled={!image || loading}
        className="w-full py-3 rounded-xl font-semibold text-white transition-all mb-6
          bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            AI 分析中...
          </span>
        ) : '开始分析'}
      </button>

      {/* Error */}
      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-xl p-4 text-red-300 mb-6">{error}</div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-6">
          {/* Main Prompt */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-white">
                {FORMats.find(f => f.key === format)?.label} 提示词
              </h2>
              <button
                onClick={() => copyText(displayPrompt)}
                className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-gray-300 transition-colors"
              >
                {copied ? '已复制 ✓' : '复制'}
              </button>
            </div>
            <pre className="text-gray-200 whitespace-pre-wrap font-sans text-sm leading-relaxed bg-gray-950 rounded-lg p-4 max-h-96 overflow-y-auto">
              {displayPrompt}
            </pre>
          </div>

          {/* Chinese Prompt */}
          {result.prompt_cn && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-semibold text-white">中文提示词</h2>
                <button
                  onClick={() => copyText(result.prompt_cn)}
                  className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-gray-300 transition-colors"
                >
                  复制
                </button>
              </div>
              <pre className="text-gray-200 whitespace-pre-wrap font-sans text-sm leading-relaxed bg-gray-950 rounded-lg p-4 max-h-48 overflow-y-auto">
                {result.prompt_cn}
              </pre>
            </div>
          )}

          {/* Analysis Details */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {result.category && (
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
                <div className="text-gray-500 text-xs mb-1">品类</div>
                <div className="text-white font-medium">{result.category}</div>
              </div>
            )}
            {result.style && (
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
                <div className="text-gray-500 text-xs mb-1">风格</div>
                <div className="text-white font-medium">{result.style}</div>
              </div>
            )}
            {result.lighting && (
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
                <div className="text-gray-500 text-xs mb-1">光线</div>
                <div className="text-white font-medium">{result.lighting}</div>
              </div>
            )}
            {result.mood && (
              <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
                <div className="text-gray-500 text-xs mb-1">氛围</div>
                <div className="text-white font-medium">{result.mood}</div>
              </div>
            )}
          </div>

          {/* Color Palette */}
          {result.colors?.length > 0 && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
              <div className="text-gray-500 text-xs mb-2">提取的配色</div>
              <div className="flex gap-2">
                {result.colors.map((c, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg border border-gray-700" style={{ backgroundColor: c }} />
                    <span className="text-gray-400 text-xs font-mono">{c}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Negative Prompt */}
          {result.negative_prompt && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-2">反向提示词 (Negative Prompt)</h3>
              <p className="text-gray-300 text-sm">{result.negative_prompt}</p>
            </div>
          )}

          {/* Composition */}
          {result.composition && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-2">构图分析</h3>
              <p className="text-gray-300 text-sm">{result.composition}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
