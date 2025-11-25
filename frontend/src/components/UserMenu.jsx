import { User, Settings, LogOut, FileText, Moon, Sun, Shield } from 'lucide-react'
import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'

function UserMenu({ isOpen, onClose }) {
    const ref = useRef(null)

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (ref.current && !ref.current.contains(event.target)) {
                onClose()
            }
        }

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside)
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [isOpen, onClose])

    if (!isOpen) return null

    const menuItems = [
        { icon: User, label: 'My Profile', action: () => console.log('Profile clicked') },
        { icon: Settings, label: 'Settings', action: () => console.log('Settings clicked') },
        { icon: FileText, label: 'Documentation', action: () => console.log('Docs clicked') },
    ]

    return (
        <div
            ref={ref}
            className="absolute top-16 right-4 w-64 bg-dark-800 border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden animate-fade-in"
        >
            <div className="p-4 border-b border-white/5 bg-dark-900/50">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary-500 to-purple-500 p-[1px]">
                        <div className="w-full h-full rounded-full bg-dark-800 flex items-center justify-center">
                            <User className="w-5 h-5 text-white" />
                        </div>
                    </div>
                    <div>
                        <h3 className="font-semibold text-white">Admin User</h3>
                        <p className="text-xs text-gray-400">admin@asura.sec</p>
                    </div>
                </div>
            </div>

            <div className="p-2">
                {menuItems.map((item, index) => (
                    <button
                        key={index}
                        onClick={() => {
                            item.action()
                            onClose()
                        }}
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-all group"
                    >
                        <item.icon className="w-4 h-4 text-gray-500 group-hover:text-primary-400 transition-colors" />
                        {item.label}
                    </button>
                ))}

                <div className="my-2 border-t border-white/5" />

                <button
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-all group"
                    onClick={() => {
                        console.log('Logout clicked')
                        onClose()
                    }}
                >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                </button>
            </div>

            <div className="p-3 bg-dark-900/30 border-t border-white/5 text-center">
                <p className="text-[10px] text-gray-600">Asura v0.3.0 • Stable</p>
            </div>
        </div>
    )
}

export default UserMenu
