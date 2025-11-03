import { Link, useLocation } from 'react-router-dom'
import { Shield, Home, FolderOpen, History, BarChart3, Moon, Sun } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

function Layout({ children }) {
  const location = useLocation()
  const { isDark, toggleTheme } = useTheme()
  
  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 transition-colors">
      <header className="bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-700 dark:from-slate-800 dark:via-slate-800 dark:to-slate-800 text-white shadow-2xl border-b-4 border-purple-400 dark:border-blue-500 transition-all">
        <div className="container mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-4 hover:opacity-90 transition-all group">
              <div className="p-2 bg-white/10 rounded-xl backdrop-blur group-hover:bg-white/20 transition-all">
                <Shield size={40} className="group-hover:scale-110 transition-transform" />
              </div>
              <div>
                <h1 className="text-3xl font-black tracking-tight">ASURA</h1>
                <p className="text-xs font-medium text-purple-200 dark:text-gray-400">SecureLab v0.3.0</p>
              </div>
            </Link>
            
            <div className="flex items-center gap-3">
              <nav className="flex gap-2">
                <Link
                  to="/"
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all font-medium ${
                    isActive('/') 
                      ? 'bg-white/20 dark:bg-blue-600/50 shadow-lg backdrop-blur' 
                      : 'hover:bg-white/10 dark:hover:bg-slate-700'
                  }`}
                >
                  <Home size={20} />
                  <span>Dashboard</span>
                </Link>
                
                <Link
                  to="/projects"
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all font-medium ${
                    isActive('/projects') 
                      ? 'bg-white/20 dark:bg-blue-600/50 shadow-lg backdrop-blur' 
                      : 'hover:bg-white/10 dark:hover:bg-slate-700'
                  }`}
                >
                  <FolderOpen size={20} />
                  <span>Projects</span>
                </Link>
                
                <Link
                  to="/history"
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all font-medium ${
                    isActive('/history') 
                      ? 'bg-white/20 dark:bg-blue-600/50 shadow-lg backdrop-blur' 
                      : 'hover:bg-white/10 dark:hover:bg-slate-700'
                  }`}
                >
                  <History size={20} />
                  <span>History</span>
                </Link>
              </nav>
              
              <button
                onClick={toggleTheme}
                className="p-2.5 rounded-xl hover:bg-white/10 dark:hover:bg-slate-700 transition-all"
                title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
              >
                {isDark ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      <footer className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-slate-900 dark:to-slate-800 border-t-2 border-purple-200 dark:border-slate-700 mt-12 transition-colors">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Shield size={24} className="text-purple-600 dark:text-blue-400" />
              <div>
                <p className="font-bold text-gray-900 dark:text-white">ASURA SecureLab v0.3.0</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">100% Local & Private Security Testing</p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-center gap-2">
                <Shield size={16} className="text-red-500 dark:text-blue-400" />
                <span>Security Scanning</span>
              </div>
              <div className="flex items-center gap-2">
                <BarChart3 size={16} className="text-blue-500 dark:text-blue-400" />
                <span>Code Metrics</span>
              </div>
            </div>
          </div>
          <div className="text-center mt-4 text-xs text-gray-500 dark:text-gray-400">
            Built with ❤️ for developers who care about security
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout
