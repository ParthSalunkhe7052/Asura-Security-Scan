import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Shield, Home, FolderOpen, History, Menu, X, Bell, User, ChevronRight, Play, Search } from 'lucide-react'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'
import Notifications from './Notifications'
import UserMenu from './UserMenu'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function Layout({ children }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)

  const isActive = (path) => location.pathname === path

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/projects', icon: FolderOpen, label: 'Projects' },
    { path: '/history', icon: History, label: 'Scan History' },
  ]

  // Breadcrumbs Logic
  const getBreadcrumbs = () => {
    const path = location.pathname
    if (path === '/') return ['Dashboard']
    if (path === '/projects') return ['Dashboard', 'Projects']
    if (path === '/history') return ['Dashboard', 'Scan History']
    if (path.startsWith('/security/')) return ['Dashboard', 'Projects', 'Scan Results']
    if (path.startsWith('/metrics/')) return ['Dashboard', 'Projects', 'Metrics']
    return ['Dashboard']
  }

  // Load unread count
  const loadUnreadCount = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/notifications?unread_only=true`)
      setUnreadCount(response.data.unread_count || 0)
    } catch (error) {
      console.error('Failed to load unread count:', error)
    }
  }

  useEffect(() => {
    loadUnreadCount()
    const interval = setInterval(loadUnreadCount, 10000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (!isNotificationsOpen) loadUnreadCount()
  }, [isNotificationsOpen])

  return (
    <div className="min-h-screen bg-dark-900 text-gray-100 flex overflow-hidden bg-grid-pattern font-sans selection:bg-primary-500/30">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: isSidebarOpen ? 280 : 80 }}
        className={clsx(
          "fixed inset-y-0 left-0 z-50 bg-dark-800/80 backdrop-blur-xl border-r border-white/5 flex flex-col transition-all duration-300 ease-in-out lg:static",
          !isSidebarOpen && "items-center"
        )}
      >
        {/* Logo Area */}
        <div className={clsx("h-20 flex items-center border-b border-white/5", isSidebarOpen ? "px-6" : "justify-center")}>
          <Link to="/" className="flex items-center gap-3 group relative">
            <div className="relative">
              <div className="absolute inset-0 bg-primary-500 blur-xl opacity-20 group-hover:opacity-50 transition-opacity duration-500" />
              <Shield className="w-9 h-9 text-primary-500 relative z-10 drop-shadow-[0_0_10px_rgba(14,165,233,0.5)]" />
            </div>
            {isSidebarOpen && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                <h1 className="text-2xl font-bold tracking-wider text-white font-mono">ASURA</h1>
                <p className="text-[10px] text-primary-400 font-mono tracking-[0.2em] uppercase">SecureLab v0.3.0</p>
              </motion.div>
            )}
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-8 space-y-2 px-3">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                "flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-300 group relative overflow-hidden",
                isActive(item.path)
                  ? "bg-primary-500/10 text-primary-400 shadow-[0_0_20px_rgba(14,165,233,0.15)] border border-primary-500/20"
                  : "text-gray-400 hover:bg-white/5 hover:text-white border border-transparent"
              )}
            >
              {isActive(item.path) && (
                <motion.div
                  layoutId="activeNav"
                  className="absolute inset-0 bg-primary-500/5 rounded-xl"
                  initial={false}
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
              <item.icon className={clsx(
                "w-6 h-6 transition-colors duration-300 relative z-10",
                isActive(item.path) ? "text-primary-400 drop-shadow-[0_0_8px_rgba(14,165,233,0.5)]" : "text-gray-500 group-hover:text-white"
              )} />
              {isSidebarOpen && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="font-medium tracking-wide relative z-10"
                >
                  {item.label}
                </motion.span>
              )}
              {isActive(item.path) && isSidebarOpen && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-400 shadow-[0_0_10px_rgba(56,189,248,1)] relative z-10" />
              )}
            </Link>
          ))}
        </nav>

        {/* User Profile (Bottom) */}
        <div className="p-4 border-t border-white/5">
          <div className={clsx(
            "bg-gradient-to-br from-dark-700/50 to-dark-800/50 rounded-2xl border border-white/5 transition-all duration-300 hover:border-white/10 group cursor-pointer",
            isSidebarOpen ? "p-4" : "p-2 aspect-square flex items-center justify-center"
          )}>
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary-500 to-purple-500 p-[1px]">
                  <div className="w-full h-full rounded-full bg-dark-800 flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-dark-800 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
              </div>

              {isSidebarOpen && (
                <div className="overflow-hidden">
                  <p className="text-sm font-bold text-white truncate group-hover:text-primary-400 transition-colors">Parth Salunkhe</p>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider">Developer License</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden relative">
        {/* Header */}
        <header className="h-20 bg-dark-900/80 backdrop-blur-md border-b border-white/5 flex items-center justify-between px-8 z-40 sticky top-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors lg:hidden"
            >
              {isSidebarOpen ? <X /> : <Menu />}
            </button>

            {/* Breadcrumbs */}
            <nav className="hidden md:flex items-center gap-2 text-sm">
              {getBreadcrumbs().map((crumb, index, arr) => (
                <div key={index} className="flex items-center gap-2">
                  <span className={clsx(
                    "font-medium",
                    index === arr.length - 1 ? "text-white text-glow" : "text-gray-500"
                  )}>
                    {crumb}
                  </span>
                  {index < arr.length - 1 && <ChevronRight className="w-4 h-4 text-gray-600" />}
                </div>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-6">
            {/* Global Actions */}
            <button
              onClick={() => navigate('/projects')}
              className="hidden md:flex items-center gap-2 px-4 py-2 bg-primary-500/10 text-primary-400 rounded-lg border border-primary-500/20 hover:bg-primary-500/20 hover:shadow-[0_0_15px_rgba(14,165,233,0.3)] transition-all duration-300 group"
            >
              <Play className="w-4 h-4 fill-current group-hover:scale-110 transition-transform" />
              <span className="font-medium text-sm">Quick Scan</span>
            </button>

            <div className="h-8 w-px bg-white/10" />

            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                className="p-2.5 text-gray-400 hover:text-white hover:bg-white/5 rounded-full transition-all duration-300 relative group"
              >
                <Bell className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                {unreadCount > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-dark-900 animate-pulse" />
                )}
              </button>
              <Notifications isOpen={isNotificationsOpen} onClose={() => setIsNotificationsOpen(false)} />
            </div>
          </div>
        </header>

        {/* Page Content with Transition */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 lg:p-10 scroll-smooth relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="max-w-7xl mx-auto h-full"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default Layout
