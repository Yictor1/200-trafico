'use client'

import { Code, Sparkles, Plus } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'
import { useWorkers } from '@/features/workers/hooks/useWorkers'
import { WorkerCard } from '@/features/workers/components/WorkerCard'
import { Button } from '@/shared/components/Button'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'

export default function WorkersPage() {
    const { data: workers, isLoading } = useWorkers()

    return (
        <div className="min-h-screen bg-dark-900">
            {/* Header */}
            <header className="glass border-b border-primary-500/20">
                <div className="container mx-auto px-6 py-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-xl bg-gradient-primary flex items-center justify-center">
                                <Sparkles className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-white">Trafico Admin</h1>
                                <p className="text-sm text-slate-400">Panel de Administración</p>
                            </div>
                        </div>

                        <nav className="flex gap-6">
                            <Link
                                href="/"
                                className="text-slate-400 hover:text-primary-400 transition-colors font-medium"
                            >
                                Modelos
                            </Link>
                            <Link
                                href="/platforms"
                                className="text-slate-400 hover:text-primary-400 transition-colors font-medium"
                            >
                                Plataformas
                            </Link>
                            <Link
                                href="/workers"
                                className="text-white hover:text-primary-400 transition-colors font-medium"
                            >
                                Workers
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-8">
                <div className="glass rounded-2xl p-6 glass-hover">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-2xl font-bold text-white mb-2">Workers</h2>
                            <p className="text-slate-400">Scripts de Playwright para automatización</p>
                        </div>
                    </div>

                    {isLoading ? (
                        <LoadingSpinner />
                    ) : workers && workers.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {workers.map((worker) => (
                                <WorkerCard key={worker.nombre} worker={worker} />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-12">
                            <Code className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                            <p className="text-slate-400 mb-4">No hay workers disponibles</p>
                            <p className="text-sm text-slate-500">Los workers se generan automáticamente al capturar plataformas</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    )
}
