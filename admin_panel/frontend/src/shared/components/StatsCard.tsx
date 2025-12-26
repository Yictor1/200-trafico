import { ReactNode } from 'react'
import { clsx } from 'clsx'

interface StatsCardProps {
    title: string
    value: string | number
    icon: ReactNode
    gradient: string
}

export function StatsCard({ title, value, icon, gradient }: StatsCardProps) {
    return (
        <div className="glass rounded-xl p-6 glass-hover animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm text-slate-400 mb-1">{title}</p>
                    <p className="text-3xl font-bold text-white">{value}</p>
                </div>
                <div className={clsx(
                    'w-14 h-14 rounded-xl flex items-center justify-center',
                    'bg-gradient-to-br',
                    gradient
                )}>
                    <div className="text-white">
                        {icon}
                    </div>
                </div>
            </div>
        </div>
    )
}
