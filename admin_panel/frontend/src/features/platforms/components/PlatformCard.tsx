'use client'

import { CheckCircle, XCircle } from 'lucide-react'
import { Platform } from '@/shared/types/api'

interface PlatformCardProps {
    platform: Platform
}

export function PlatformCard({ platform }: PlatformCardProps) {
    return (
        <div className="glass rounded-xl p-4 glass-hover">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-base font-bold text-white capitalize">{platform.nombre}</h3>
                    <div className="flex items-center gap-2 mt-1">
                        {platform.has_worker ? (
                            <div className="flex items-center gap-1 text-green-400">
                                <CheckCircle className="w-3 h-3" />
                                <span className="text-xs">Worker disponible</span>
                            </div>
                        ) : (
                            <div className="flex items-center gap-1 text-slate-500">
                                <XCircle className="w-3 h-3" />
                                <span className="text-xs">Sin worker</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
