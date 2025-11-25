import { X, CheckCircle, AlertTriangle, Info, Clock, XCircle, Play } from 'lucide-react'
import clsx from 'clsx'
import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function Notifications({ isOpen, onClose }) {
    const ref = useRef(null)
    const navigate = useNavigate()
    const [notifications, setNotifications] = useState([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (ref.current && !ref.current.contains(event.target)) {
                onClose()
            }
        }

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside)
            loadNotifications()
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [isOpen, onClose])

    const loadNotifications = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE_URL}/api/notifications`)
            setNotifications(response.data.notifications || [])
        } catch (error) {
            console.error('Failed to load notifications:', error)
        } finally {
            setLoading(false)
        }
    }

    const markAsRead = async (notificationId) => {
        try {
            await axios.post(`${API_BASE_URL}/api/notifications/${notificationId}/read`)
            // Update local state
            setNotifications(prev =>
                prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
            )
        } catch (error) {
            console.error('Failed to mark notification as read:', error)
        }
    }

    const markAllAsRead = async () => {
        try {
            await axios.post(`${API_BASE_URL}/api/notifications/mark-all-read`)
            setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
        } catch (error) {
            console.error('Failed to mark all as read:', error)
        }
    }

    const handleNotificationClick = (notification) => {
        // Mark as read
        if (!notification.is_read) {
            markAsRead(notification.id)
        }

        // Navigate to scan if available
        if (notification.scan_id) {
            navigate(`/security/${notification.scan_id}`)
            onClose()
        }
    }

    const getTimeAgo = (timestamp) => {
        if (!timestamp) return 'Just now'

        const now = new Date()
        const past = new Date(timestamp)
        const diffMs = now - past
        const diffMins = Math.floor(diffMs / 60000)

        if (diffMins < 1) return 'Just now'
        if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`

        const diffHours = Math.floor(diffMins / 60)
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`

        const diffDays = Math.floor(diffHours / 24)
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    }

    const getIcon = (type) => {
        switch (type) {
            case 'scan_completed':
                return <CheckCircle className="w-5 h-5 text-green-500" />
            case 'scan_failed':
                return <XCircle className="w-5 h-5 text-red-500" />
            case 'scan_started':
                return <Play className="w-5 h-5 text-blue-500" />
            default:
                return <Info className="w-5 h-5 text-gray-500" />
        }
    }

    if (!isOpen) return null

    return (
        <div
            ref={ref}
            className="absolute top-16 right-20 w-80 md:w-96 bg-dark-800 border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden animate-fade-in"
        >
            <div className="p-4 border-b border-white/5 flex items-center justify-between bg-dark-900/50">
                <h3 className="font-semibold text-white">Notifications</h3>
                <button
                    onClick={onClose}
                    className="text-gray-400 hover:text-white transition-colors"
                >
                    <X className="w-4 h-4" />
                </button>
            </div>

            <div className="max-h-[400px] overflow-y-auto">
                {loading ? (
                    <div className="p-8 text-center text-gray-500">
                        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500 mx-auto"></div>
                        <p className="mt-2 text-sm">Loading notifications...</p>
                    </div>
                ) : notifications.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        <Info className="w-12 h-12 mx-auto mb-3 opacity-30" />
                        <p className="text-sm">No notifications yet</p>
                    </div>
                ) : (
                    notifications.map((notification) => (
                        <div
                            key={notification.id}
                            className={clsx(
                                "p-4 border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group",
                                !notification.is_read && "bg-primary-500/5"
                            )}
                            onClick={() => handleNotificationClick(notification)}
                        >
                            <div className="flex gap-3">
                                <div className="mt-1">
                                    {getIcon(notification.type)}
                                </div>
                                <div className="flex-1">
                                    <div className="flex justify-between items-start mb-1">
                                        <h4 className={clsx(
                                            "text-sm font-medium",
                                            !notification.is_read ? "text-white" : "text-gray-400"
                                        )}>
                                            {notification.title}
                                        </h4>
                                        <span className="text-[10px] text-gray-500 whitespace-nowrap flex items-center gap-1">
                                            <Clock className="w-3 h-3" />
                                            {getTimeAgo(notification.created_at)}
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-400 leading-relaxed group-hover:text-gray-300">
                                        {notification.message}
                                    </p>
                                    {!notification.is_read && (
                                        <div className="mt-2">
                                            <span className="inline-block w-2 h-2 rounded-full bg-primary-500"></span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {notifications.length > 0 && (
                <div className="p-3 bg-dark-900/50 border-t border-white/5 text-center">
                    <button
                        onClick={markAllAsRead}
                        className="text-xs text-primary-400 hover:text-primary-300 font-medium transition-colors"
                    >
                        Mark all as read
                    </button>
                </div>
            )}
        </div>
    )
}

export default Notifications
