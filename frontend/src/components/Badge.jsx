import React from 'react';
import clsx from 'clsx';

const Badge = ({ children, variant = 'default', className }) => {
    const variants = {
        default: 'bg-gray-800 text-gray-300 border border-gray-700',
        critical: 'badge-critical',
        high: 'badge-high',
        medium: 'badge-medium',
        low: 'badge-low',
        success: 'bg-green-500/10 text-green-400 border border-green-500/20 shadow-[0_0_10px_rgba(34,197,94,0.1)]',
        info: 'bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-[0_0_10px_rgba(59,130,246,0.1)]',
    };

    return (
        <span className={clsx('badge', variants[variant], className)}>
            {children}
        </span>
    );
};

export default Badge;
