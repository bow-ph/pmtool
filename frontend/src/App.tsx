import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './api/client'
import { ThemeProvider } from './contexts/ThemeContext'
import MainLayout from './layouts/MainLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ProjectAnalysis from './pages/ProjectAnalysis'
import PackageSelection from './pages/PackageSelection'
import PackageAdmin from './pages/admin/PackageAdmin'
import AccountSettings from './pages/AccountSettings'
import ResetPassword from './pages/ResetPassword'
import SignUp from './pages/SignUp'
import { Toaster } from 'react-hot-toast'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="analysis" element={<ProjectAnalysis />} />
              <Route path="packages" element={<PackageSelection />} />
              <Route path="admin/packages" element={<PackageAdmin />} />
              <Route path="account" element={<AccountSettings />} />
            </Route>
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
          <Toaster position="top-right" />
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
