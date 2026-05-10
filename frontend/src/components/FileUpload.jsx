import { useRef, useState } from 'react';

export default function FileUpload({ onUpload }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [fileName, setFileName] = useState('');

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) { setFileName(file.name); onUpload(file); }
  };

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) { setFileName(file.name); onUpload(file); }
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition ${
        dragging ? 'border-indigo-400 bg-indigo-400/10' : 'border-gray-700 hover:border-gray-500'
      }`}
    >
      <input ref={inputRef} type="file" accept=".csv,.json,.xlsx" onChange={handleChange} className="hidden" />
      <div className="text-3xl mb-3">📁</div>
      {fileName ? (
        <div><p className="text-sm font-medium">{fileName}</p><p className="text-xs text-gray-500 mt-1">点击重新选择</p></div>
      ) : (
        <div><p className="text-sm text-gray-400">拖拽文件到此处或点击上传</p><p className="text-xs text-gray-600 mt-1">支持 CSV / JSON 格式</p></div>
      )}
    </div>
  );
}
