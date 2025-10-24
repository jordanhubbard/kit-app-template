import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  children?: React.ReactNode;
}

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export const Card: React.FC<CardProps> = ({
  hover = false,
  padding = 'md',
  children,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`
        bg-dark-card rounded-lg border border-gray-700
        ${paddingClasses[padding]}
        ${hover ? 'hover:bg-dark-hover hover:border-gray-600 transition-all duration-200 cursor-pointer' : ''}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;

