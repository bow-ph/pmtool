import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './api/client'
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import ProjectAnalysis from './pages/ProjectAnalysis'
import PackageSelection from './pages/PackageSelection'
import PackageAdmin from './pages/admin/PackageAdmin'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="analysis" element={<ProjectAnalysis />} />
            <Route path="packages" element={<PackageSelection />} />
            <Route path="admin/packages" element={<PackageAdmin />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
