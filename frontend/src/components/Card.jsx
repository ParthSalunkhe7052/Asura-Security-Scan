import React from 'react';
import clsx from 'clsx';

const Card = ({ children, className, hover = false, ...props }) => {
    return (
        <div
            className={clsx(
                'glass-card rounded-xl p-6',
                hover && 'hover:translate-y-[-2px] hover:shadow-2xl hover:shadow-primary-900/20',
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
};

export default Card;
