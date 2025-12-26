'use client'

import { Layers, Plus, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'
import { usePlatforms } from '@/features/platforms/hooks/usePlatforms'
import { PlatformCard } from '@/features/platforms/components/PlatformCard'
import { AddPlatformModal } from '@/features/platforms/components/AddPlatformModal'
import { Button } from '@/shared/components/Button'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'

export default function PlatformsPage() {
    const { data: platforms, isLoading } = usePlatforms()
    const [isAddModalOpen, setIsAddModalOpen] = useState(false)

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
                                className="text-white hover:text-primary-400 transition-colors font-medium"
                            >
                                Plataformas
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
                            <h2 className="text-2xl font-bold text-white mb-2">Plataformas</h2>
                            <p className="text-slate-400">Gestiona las plataformas de publicación</p>
                        </div>
                        <Button onClick={() => setIsAddModalOpen(true)} size="sm">
                            <Plus className="w-4 h-4 mr-2" />
                            Agregar Plataforma
                        </Button>
                    </div>

                    {isLoading ? (
                        <LoadingSpinner />
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {platforms?.map((platform) => (
                                <PlatformCard key={platform.nombre} platform={platform} />
                            ))}
                        </div>
                    )}
                </div>
            </main>

            <AddPlatformModal
                isOpen={isAddModalOpen}
                onClose={() => setIsAddModalOpen(false)}
            />
        </div>
    )
}
