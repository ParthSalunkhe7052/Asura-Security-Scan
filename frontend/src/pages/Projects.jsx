import { useState, useEffect } from 'react'
import { Plus, Folder, Trash2, Edit2, ExternalLink } from 'lucide-react'
import { projectsApi } from '../lib/api'

function Projects() {
  const [projects, setProjects] = useState([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    path: '',
    description: ''
  })

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const response = await projectsApi.getAll()
      setProjects(response.data)
    } catch (error) {
      console.error('Failed to load projects:', error)
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
      } else {
        await projectsApi.create(formData)
      }
      
      loadProjects()
      closeModal()
    } catch (error) {
      console.error('Failed to save project:', error)
      alert(error.response?.data?.detail || 'Failed to save project')
    }
  }

  const handleDelete = async (projectId) => {
    if (!confirm('Are you sure you want to delete this project? This will also delete all associated scans.')) {
      return
    }

    try {
      await projectsApi.delete(projectId)
      loadProjects()
    } catch (error) {
      console.error('Failed to delete project:', error)
      alert('Failed to delete project')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Projects</h1>
          <p className="text-gray-600">Manage your code projects</p>
        </div>
        
        <button
          onClick={() => openModal()}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          New Project
        </button>
      </div>

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <div className="card text-center py-12">
          <Folder className="mx-auto text-gray-400 mb-4" size={64} />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No projects yet</h3>
          <p className="text-gray-600 mb-6">Create your first project to get started with security scanning</p>
          <button
            onClick={() => openModal()}
            className="btn-primary"
          >
            Create Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map(project => (
            <div key={project.id} className="card hover:shadow-lg transition">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Folder className="text-purple-600" size={24} />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-gray-900">{project.name}</h3>
                    <p className="text-xs text-gray-500">
                      {new Date(project.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  {project.description || 'No description'}
                </p>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <ExternalLink size={14} />
                  <span className="truncate">{project.path}</span>
                </div>
              </div>

              {project.total_scans !== undefined && (
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Total Scans</span>
                    <span className="font-semibold">{project.total_scans}</span>
                  </div>
                  {project.latest_health_score && (
                    <div className="flex items-center justify-between text-sm mt-2">
                      <span className="text-gray-600">Health Score</span>
                      <span className={`font-semibold ${
                        project.latest_health_score >= 80 ? 'text-green-600' :
                        project.latest_health_score >= 60 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {project.latest_health_score.toFixed(0)}%
                      </span>
                    </div>
                  )}
                </div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={() => openModal(project)}
                  className="flex-1 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition flex items-center justify-center gap-2"
                >
                  <Edit2 size={16} />
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(project.id)}
                  className="px-3 py-2 text-sm bg-red-100 hover:bg-red-200 text-red-600 rounded-lg transition"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4">
              {editingProject ? 'Edit Project' : 'New Project'}
            </h2>

            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                  placeholder="my-awesome-app"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Project Path *
                </label>
                <input
                  type="text"
                  value={formData.path}
                  onChange={(e) => setFormData({ ...formData, path: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                  placeholder="C:\Users\...\my-project"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Absolute path to your project directory
                </p>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  rows="3"
                  placeholder="Optional description..."
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={closeModal}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 btn-primary"
                >
                  {editingProject ? 'Save Changes' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Projects
