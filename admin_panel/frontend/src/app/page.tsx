'use client'

import { Users, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { ModelList } from '@/features/models/components/ModelList'
import { StatsCard } from '@/shared/components/StatsCard'

export default function HomePage() {
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
                                className="text-white hover:text-primary-400 transition-colors font-medium"
                            >
                                Modelos
                            </Link>
                            <Link
                                href="/platforms"
                                className="text-slate-400 hover:text-primary-400 transition-colors font-medium"
                            >
                                Plataformas
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-8">
                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-1 gap-6 mb-8">
                    <StatsCard
                        title="Modelos"
                        value="0"
                        icon={<Users className="w-6 h-6" />}
                        gradient="from-primary-500 to-primary-600"
                    />
                </div>

                {/* Models Section */}
                <div className="glass rounded-2xl p-6 glass-hover">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold text-white">Modelos</h2>
                    </div>

                    <ModelList />
                </div>
            </main>
        </div>
    )
}
