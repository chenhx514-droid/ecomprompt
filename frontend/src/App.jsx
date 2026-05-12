import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Detail from './pages/Detail'
import Generate from './pages/Generate'
import Trends from './pages/Trends'
import Import from './pages/Import'
import Collect from './pages/Collect'
import ImageToPrompt from './pages/ImageToPrompt'
import Login from './pages/Login'
import Register from './pages/Register'

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-950">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/prompt/:id" element={<Detail />} />
            <Route path="/generate" element={<Generate />} />
            <Route path="/image-to-prompt" element={<ImageToPrompt />} />
            <Route path="/trends" element={<Trends />} />
            <Route path="/import" element={<Import />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/collect" element={
              <ProtectedRoute><Collect /></ProtectedRoute>
            } />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  )
}
