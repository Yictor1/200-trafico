'use client'

import { Globe, Edit, Trash2, BarChart3 } from 'lucide-react'
import { Model } from '@/shared/types/api'
import { Button } from '@/shared/components/Button'
import { useState } from 'react'
import { useDeleteModel } from '../hooks/useModels'

interface ModelCardProps {
    model: Model
    onOpenBrowser?: (modelo: string) => void
    onEdit?: (model: Model) => void
    onViewMetrics?: (modelo: string) => void
}

export function ModelCard({ model, onOpenBrowser, onEdit, onViewMetrics }: ModelCardProps) {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const profilePhotoPath = model.profile_photo 
        ? `${API_URL}/api/models/${model.modelo}/profile-photo`
        : null
    const [imageError, setImageError] = useState(false)
    const deleteModel = useDeleteModel()
    const [showConfirmDelete, setShowConfirmDelete] = useState(false)

    const handleDelete = () => {
        if (showConfirmDelete) {
            deleteModel.mutate(model.modelo)
            setShowConfirmDelete(false)
        } else {
            setShowConfirmDelete(true)
            setTimeout(() => setShowConfirmDelete(false), 3000)
        }
    }

    return (
        <div className="glass rounded-xl p-5 glass-hover">
            <div className="flex flex-col items-center text-center mb-4">
                {/* Foto de perfil circular */}
                <div className="w-24 h-24 rounded-full overflow-hidden bg-gradient-to-br from-primary-500 to-secondary-500 mb-3 flex items-center justify-center">
                    {profilePhotoPath && !imageError ? (
                        <img
                            src={profilePhotoPath}
                            alt={model.modelo}
                            className="w-full h-full object-cover"
                            onError={() => setImageError(true)}
                        />
                    ) : (
                        <span className="text-white text-2xl font-bold">
                            {model.modelo.charAt(0).toUpperCase()}
                        </span>
                    )}
                </div>

                {/* Nombre del modelo */}
                <h3 className="text-lg font-bold text-white mb-2">{model.modelo}</h3>

                {/* Horario */}
                <div className="flex items-center gap-2 text-sm mb-4">
                    <span className="text-slate-400">Horario:</span>
                    <span className="text-slate-300">{model.hora_inicio}</span>
                    <span className="text-slate-500">({model.ventana_horas}h)</span>
                </div>
            </div>

            {/* Botones */}
            <div className="flex flex-col gap-2">
                <Button
                    variant="primary"
                    size="sm"
                    className="w-full"
                    onClick={() => onOpenBrowser?.(model.modelo)}
                >
                    <Globe className="w-4 h-4 mr-2" />
                    🌐 Abrir Navegador
                </Button>
                {model.striphours_url && (
                    <Button
                        variant="secondary"
                        size="sm"
                        className="w-full"
                        onClick={() => onViewMetrics?.(model.modelo)}
                    >
                        <BarChart3 className="w-4 h-4 mr-2" />
                        📊 Vista Avanzada
                    </Button>
                )}
                <Button
                    variant="secondary"
                    size="sm"
                    className="w-full"
                    onClick={() => onEdit?.(model)}
                >
                    <Edit className="w-4 h-4 mr-2" />
                    ✏️ Editar
                </Button>
                <Button
                    variant={showConfirmDelete ? 'danger' : 'secondary'}
                    size="sm"
                    className="w-full"
                    onClick={handleDelete}
                    isLoading={deleteModel.isPending}
                >
                    <Trash2 className="w-4 h-4 mr-2" />
                    {showConfirmDelete ? '¿Eliminar?' : '🗑️ Eliminar'}
                </Button>
            </div>
        </div>
    )
}
