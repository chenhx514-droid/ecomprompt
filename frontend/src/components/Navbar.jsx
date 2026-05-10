import { Link, useLocation } from 'react-router-dom';

const links = [
  { to: '/', label: '提示词库' },
  { to: '/generate', label: 'AI生成' },
  { to: '/trends', label: '趋势' },
  { to: '/import', label: '数据导入' },
];

export default function Navbar() {
  const { pathname } = useLocation();
  return (
    <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-indigo-400">
          EcomPrompt
        </Link>
        <div className="flex gap-1">
          {links.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`px-3 py-1.5 rounded text-sm transition ${
                pathname === to
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-gray-800'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
