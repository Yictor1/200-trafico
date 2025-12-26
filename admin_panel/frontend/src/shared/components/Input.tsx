import { InputHTMLAttributes } from 'react'
import { clsx } from 'clsx'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string
    error?: string
    helperText?: string
}

export function Input({ label, error, helperText, className, ...props }: InputProps) {
    return (
        <div className="w-full">
            {label && (
                <label className="block text-sm font-medium text-slate-300 mb-2">
                    {label}
                </label>
            )}

            <input
                className={clsx(
                    'w-full px-4 py-3 rounded-lg',
                    'bg-dark-800 border border-primary-500/30',
                    'text-white placeholder-slate-500',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                    'transition-all duration-200',
                    error && 'border-red-500 focus:ring-red-500',
                    className
                )}
                {...props}
            />

            {error && (
                <p className="mt-2 text-sm text-red-400">{error}</p>
            )}

            {helperText && !error && (
                <p className="mt-2 text-sm text-slate-400">{helperText}</p>
            )}
        </div>
    )
}
