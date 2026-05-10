import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Detail from './pages/Detail'
import Generate from './pages/Generate'
import Trends from './pages/Trends'
import Import from './pages/Import'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/prompt/:id" element={<Detail />} />
          <Route path="/generate" element={<Generate />} />
          <Route path="/trends" element={<Trends />} />
          <Route path="/import" element={<Import />} />
        </Routes>
      </main>
    </div>
  )
}
