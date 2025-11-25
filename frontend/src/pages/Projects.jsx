import { useState, useEffect } from 'react'
import { Plus, Folder, Trash2, Edit2, Search, Code, Calendar, Shield, Target, ChevronRight, MoreVertical } from 'lucide-react'
import { projectsApi } from '../lib/api'
import { useToast } from '../contexts/ToastContext'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'

function Projects() {
  const [projects, setProjects] = useState([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    path: '',
    description: ''
  })
  const [searchQuery, setSearchQuery] = useState('')
  const toast = useToast()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setLoading(true)
      const response = await projectsApi.getAll()
      setProjects(response.data)
    } catch (error) {
      console.error('Failed to load projects:', error)
      toast.error('Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  const openModal = (project = null) => {
    if (project) {
      setEditingProject(project)
      setFormData({
        name: project.name,
        path: project.path,
        description: project.description || ''
      })
    } else {
      setEditingProject(null)
      setFormData({ name: '', path: '', description: '' })
    }
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditingProject(null)
    setFormData({ name: '', path: '', description: '' })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingProject) {
        await projectsApi.update(editingProject.id, formData)
        toast.success('Project updated successfully')
      } else {
        await projectsApi.create(formData)
        toast.success('Project created successfully')
      }
      loadProjects()
      closeModal()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save project')
    }
  }

  const handleDelete = async (projectId) => {
    if (!confirm('Are you sure you want to delete this project? This will also delete all associated scans.')) return
    try {
      await projectsApi.delete(projectId)
      toast.success('Project deleted successfully')
      loadProjects()
    } catch (error) {
      toast.error('Failed to delete project')
    }
  }

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Projects</h1>
          <p className="text-gray-400 mt-1">Manage and monitor your code repositories</p>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => openModal()}
          className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-primary-600 to-primary-500 text-white rounded-xl font-medium shadow-[0_0_20px_rgba(14,165,233,0.3)] hover:shadow-[0_0_30px_rgba(14,165,233,0.5)] transition-all"
        >
          <Plus className="w-5 h-5" />
          <span>New Project</span>
        </motion.button>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-500" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-3 border border-white/10 rounded-xl leading-5 bg-dark-800/50 text-gray-300 placeholder-gray-500 focus:outline-none focus:bg-dark-800 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 sm:text-sm transition-colors"
          placeholder="Search projects by name or description..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
        </div>
      ) : projects.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center py-20 text-center bg-dark-800/30 rounded-3xl border border-white/5 border-dashed"
        >
          <div className="w-24 h-24 rounded-full bg-dark-800 flex items-center justify-center mb-6 border border-white/5 shadow-inner">
            <Folder className="w-10 h-10 text-gray-600" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No projects found</h3>
          <p className="text-gray-400 max-w-md mb-8">
            Create your first project to get started with security scanning and code analysis.
          </p>
          <button
            onClick={() => openModal()}
            className="text-primary-400 hover:text-primary-300 font-medium flex items-center gap-2"
          >
            Create Project <ChevronRight className="w-4 h-4" />
          </button>
        </motion.div>
      ) : (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredProjects.map(project => (
            <motion.div
              key={project.id}
              variants={item}
              className="group bg-dark-800/40 backdrop-blur-md border border-white/5 rounded-2xl p-6 hover:border-primary-500/30 hover:bg-dark-800/60 transition-all duration-300 relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-6 opacity-0 group-hover:opacity-10 transition-opacity duration-500">
                <Code className="w-32 h-32 text-primary-500 transform rotate-12 translate-x-8 -translate-y-8" />
              </div>

              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-dark-700 to-dark-800 border border-white/5 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                      <Code className="w-6 h-6 text-primary-400" />
                    </div>
                    <div>
                      <h3 className="font-bold text-lg text-white group-hover:text-primary-400 transition-colors line-clamp-1">
                        {project.name}
                      </h3>
                      <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(project.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-1">
                    <button
                      onClick={() => openModal(project)}
                      className="p-2 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button
                      onClick={() => handleDelete(project.id)}
                      className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>

                <p className="text-sm text-gray-400 line-clamp-2 mb-6 min-h-[2.5rem]">
                  {project.description || 'No description provided for this project.'}
                </p>

                <div className="bg-dark-900/50 rounded-lg p-3 border border-white/5 mb-6 flex items-center gap-3">
                  <Folder className="w-4 h-4 text-gray-500 shrink-0" />
                  <span className="text-xs font-mono text-gray-400 truncate">{project.path}</span>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-white/5">
                  <div className="flex items-center gap-6">
                    <div>
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Scans</p>
                      <p className="text-lg font-bold text-white">{project.total_scans || 0}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Health</p>
                      <p className={clsx(
                        "text-lg font-bold",
                        !project.latest_health_score ? "text-gray-500" :
                          project.latest_health_score >= 80 ? "text-green-400" :
                            project.latest_health_score >= 60 ? "text-yellow-400" : "text-red-400"
                      )}>
                        {project.latest_health_score ? `${project.latest_health_score.toFixed(0)}%` : 'N/A'}
                      </p>
                    </div>
                  </div>

                  <div className={clsx(
                    "w-10 h-10 rounded-full flex items-center justify-center border",
                    !project.latest_health_score ? "bg-gray-500/10 border-gray-500/20 text-gray-500" :
                      project.latest_health_score >= 80 ? "bg-green-500/10 border-green-500/20 text-green-500" :
                        project.latest_health_score >= 60 ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-500" :
                          "bg-red-500/10 border-red-500/20 text-red-500"
                  )}>
                    <Shield className="w-5 h-5" />
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/80 backdrop-blur-sm"
              onClick={closeModal}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-lg bg-dark-800 border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
            >
              <div className="p-6 border-b border-white/10 bg-gradient-to-r from-dark-800 to-dark-700">
                <h2 className="text-xl font-bold text-white">
                  {editingProject ? 'Edit Project' : 'New Project'}
                </h2>
                <p className="text-sm text-gray-400 mt-1">Configure your project settings</p>
              </div>

              <form onSubmit={handleSubmit} className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Project Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full bg-dark-900/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all"
                    required
                    placeholder="e.g. My Awesome App"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Project Path <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={formData.path}
                      onChange={(e) => setFormData({ ...formData, path: e.target.value })}
                      className="w-full bg-dark-900/50 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white font-mono text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all"
                      required
                      placeholder="C:\Users\..."
                    />
                    <Folder className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Absolute path to your project directory on this machine
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full bg-dark-900/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all min-h-[100px]"
                    placeholder="What is this project about?"
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={closeModal}
                    className="flex-1 px-4 py-3 bg-white/5 text-gray-300 rounded-xl hover:bg-white/10 hover:text-white transition-colors font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-500 transition-colors font-medium shadow-lg shadow-primary-500/20"
                  >
                    {editingProject ? 'Save Changes' : 'Create Project'}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Projects
