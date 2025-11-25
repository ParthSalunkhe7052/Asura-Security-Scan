import React from 'react';
import clsx from 'clsx';
import { Loader2 } from 'lucide-react';

const Button = ({
    children,
    variant = 'primary',
    className,
    isLoading = false,
    icon: Icon,
    ...props
}) => {
    const variants = {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        neon: 'btn-neon',
        danger: 'bg-red-500/10 text-red-500 border border-red-500/50 hover:bg-red-500/20 hover:shadow-[0_0_15px_rgba(239,68,68,0.3)] transition-all duration-300 active:scale-95 rounded-lg px-4 py-2'
    };

    return (
        <button
            className={clsx(
                'flex items-center justify-center gap-2',
                variants[variant],
                isLoading && 'opacity-70 cursor-not-allowed',
                className
            )}
            disabled={isLoading || props.disabled}
            {...props}
        >
            {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
            ) : Icon ? (
                <Icon className="w-4 h-4" />
            ) : null}
            {children}
        </button>
    );
};

export default Button;
