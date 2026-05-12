import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const publicLinks = [
  { to: '/', label: '提示词库' },
  { to: '/generate', label: 'AI生成' },
  { to: '/image-to-prompt', label: '图转提示词' },
  { to: '/trends', label: '趋势' },
  { to: '/import', label: '数据导入' },
];

export default function Navbar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuth();

  const links = user
    ? [...publicLinks, { to: '/collect', label: '收录' }]
    : publicLinks;

  return (
    <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-indigo-400">
          EcomPrompt
        </Link>
        <div className="flex items-center gap-1">
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
          <div className="w-px h-5 bg-gray-700 mx-2" />
          {user ? (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400 max-w-[160px] truncate">{user.email}</span>
              <button
                onClick={logout}
                className="px-3 py-1.5 rounded text-sm text-gray-300 hover:text-white hover:bg-gray-800 transition"
              >
                退出
              </button>
            </div>
          ) : (
            <>
              <Link
                to="/login"
                className={`px-3 py-1.5 rounded text-sm transition ${
                  pathname === '/login'
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
              >
                登录
              </Link>
              <Link
                to="/register"
                className={`px-3 py-1.5 rounded text-sm transition ${
                  pathname === '/register'
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
              >
                注册
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
