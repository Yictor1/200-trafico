'use client'

import { useState, useEffect } from 'react'
import { Modal } from '@/shared/components/Modal'
import { Button } from '@/shared/components/Button'
import { useStartAuth, useAuthStatus } from '@/features/auth/hooks/useAuth'
import { CheckCircle, Loader, AlertCircle, ExternalLink } from 'lucide-react'

interface PlatformAuthModalProps {
    isOpen: boolean
    onClose: () => void
    modelo: string
    plataformas: string[]
}

const PLATFORM_URLS: Record<string, string> = {
    'kams': 'https://kams.com/login',
    'xxxfollow': 'https://xxxfollow.com/login',
    'onlyfans': 'https://onlyfans.com',
    'fansly': 'https://fansly.com/login',
}

export function PlatformAuthModal({ isOpen, onClose, modelo, plataformas }: PlatformAuthModalProps) {
    const startAuth = useStartAuth()
    const [currentPlatformIndex, setCurrentPlatformIndex] = useState(0)
    const [sessionId, setSessionId] = useState<string | null>(null)
    const [completedPlatforms, setCompletedPlatforms] = useState<string[]>([])

    const { data: authStatus } = useAuthStatus(sessionId)

    const currentPlatform = plataformas[currentPlatformIndex]
    const allCompleted = completedPlatforms.length === plataformas.length

    useEffect(() => {
        if (authStatus?.status === 'completed' && currentPlatform) {
            // Marcar como completada
            setCompletedPlatforms(prev => [...prev, currentPlatform])
            setSessionId(null)

            // Pasar a la siguiente plataforma
            if (currentPlatformIndex < plataformas.length - 1) {
                setTimeout(() => {
                    setCurrentPlatformIndex(prev => prev + 1)
                }, 1500)
            }
        }
    }, [authStatus, currentPlatform, currentPlatformIndex, plataformas.length])

    const handleStartAuth = async () => {
        const url = PLATFORM_URLS[currentPlatform] || `https://${currentPlatform}.com/login`

        try {
            const session = await startAuth.mutateAsync({
                modelo,
                plataforma: currentPlatform,
                url
            })
            setSessionId(session.session_id)
        } catch (error) {
            console.error('Error iniciando autenticación:', error)
        }
    }

    const handleClose = () => {
        setCurrentPlatformIndex(0)
        setSessionId(null)
        setCompletedPlatforms([])
        onClose()
    }

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title="🔐 Configurar Credenciales" size="lg">
            <div className="space-y-6">
                {/* Progreso */}
                <div className="flex items-center justify-between p-4 bg-dark-800 rounded-lg">
                    <div>
                        <p className="text-sm text-slate-400">Modelo</p>
                        <p className="text-lg font-bold text-white">{modelo}</p>
                    </div>
                    <div>
                        <p className="text-sm text-slate-400">Progreso</p>
                        <p className="text-lg font-bold text-white">
                            {completedPlatforms.length} / {plataformas.length}
                        </p>
                    </div>
                </div>

                {/* Lista de plataformas */}
                <div className="space-y-2">
                    {plataformas.map((plat, index) => {
                        const isCompleted = completedPlatforms.includes(plat)
                        const isCurrent = index === currentPlatformIndex
                        const isPending = index > currentPlatformIndex

                        return (
                            <div
                                key={plat}
                                className={`p-4 rounded-lg border transition-all ${isCompleted
                                        ? 'bg-green-500/10 border-green-500/30'
                                        : isCurrent
                                            ? 'bg-primary-500/10 border-primary-500/30'
                                            : 'bg-dark-800 border-slate-700'
                                    }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        {isCompleted ? (
                                            <CheckCircle className="w-5 h-5 text-green-400" />
                                        ) : isCurrent ? (
                                            <Loader className="w-5 h-5 text-primary-400 animate-spin" />
                                        ) : (
                                            <div className="w-5 h-5 rounded-full border-2 border-slate-600" />
                                        )}
                                        <div>
                                            <p className="font-semibold text-white capitalize">{plat}</p>
                                            {isCurrent && authStatus && (
                                                <p className="text-sm text-slate-400">{authStatus.message}</p>
                                            )}
                                            {isCompleted && (
                                                <p className="text-sm text-green-400">✓ Credenciales guardadas</p>
                                            )}
                                        </div>
                                    </div>

                                    {isCurrent && !sessionId && (
                                        <Button
                                            onClick={handleStartAuth}
                                            size="sm"
                                            isLoading={startAuth.isPending}
                                        >
                                            <ExternalLink className="w-4 h-4 mr-1" />
                                            Abrir Navegador
                                        </Button>
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>

                {/* Instrucciones */}
                {sessionId && authStatus?.status === 'authenticating' && (
                    <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                        <div className="flex gap-3">
                            <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                            <div className="text-sm text-blue-300">
                                <p className="font-semibold mb-1">Instrucciones:</p>
                                <ol className="list-decimal list-inside space-y-1 text-blue-400">
                                    <li>Se abrió un navegador para <strong>{currentPlatform}</strong></li>
                                    <li>Completa el login manualmente en el navegador</li>
                                    <li>El navegador se cerrará automáticamente en 5 minutos</li>
                                    <li>Las credenciales se guardarán automáticamente</li>
                                </ol>
                            </div>
                        </div>
                    </div>
                )}

                {/* Botón final */}
                {allCompleted && (
                    <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                        <div className="flex items-center gap-3 mb-4">
                            <CheckCircle className="w-6 h-6 text-green-400" />
                            <div>
                                <p className="font-semibold text-green-300">¡Configuración Completa!</p>
                                <p className="text-sm text-green-400">
                                    Todas las credenciales han sido guardadas correctamente
                                </p>
                            </div>
                        </div>
                        <Button onClick={handleClose} className="w-full">
                            Finalizar
                        </Button>
                    </div>
                )}

                {!allCompleted && (
                    <div className="flex gap-3">
                        <Button
                            variant="secondary"
                            onClick={handleClose}
                            className="flex-1"
                        >
                            Cancelar
                        </Button>
                    </div>
                )}
            </div>
        </Modal>
    )
}
