'use client'

import { Code, FileCode, Trash2 } from 'lucide-react'
import { Worker } from '@/shared/types/api'
import { Button } from '@/shared/components/Button'
import { useDeleteWorker } from '../hooks/useWorkers'
import { useState } from 'react'

interface WorkerCardProps {
    worker: Worker
}

export function WorkerCard({ worker }: WorkerCardProps) {
    const deleteWorker = useDeleteWorker()
    const [showConfirm, setShowConfirm] = useState(false)

    const handleDelete = () => {
        if (showConfirm) {
            deleteWorker.mutate(worker.nombre)
            setShowConfirm(false)
        } else {
            setShowConfirm(true)
            setTimeout(() => setShowConfirm(false), 3000)
        }
    }

    const formatSize = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B`
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    }

    return (
        <div className="glass rounded-xl p-5 glass-hover">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        <FileCode className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-white">{worker.nombre}.js</h3>
                        <p className="text-sm text-slate-400">{worker.path}</p>
                    </div>
                </div>
            </div>

            <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">Tamaño:</span>
                    <span className="text-slate-300">{formatSize(worker.size)}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">Líneas:</span>
                    <span className="text-slate-300">{worker.lines}</span>
                </div>
            </div>

            <div className="flex gap-2">
                <Button
                    variant="secondary"
                    size="sm"
                    className="flex-1"
                    onClick={() => window.open(`/workers/${worker.nombre}`, '_blank')}
                >
                    <Code className="w-4 h-4 mr-1" />
                    Ver Código
                </Button>
                <Button
                    variant={showConfirm ? 'danger' : 'secondary'}
                    size="sm"
                    onClick={handleDelete}
                    isLoading={deleteWorker.isPending}
                >
                    <Trash2 className="w-4 h-4" />
                    {showConfirm ? '¿Seguro?' : ''}
                </Button>
            </div>
        </div>
    )
}
