'use client'

import { useState } from 'react'
import { Plus } from 'lucide-react'
import { useModels } from '../hooks/useModels'
import { ModelCard } from './ModelCard'
import { CreateModelModal } from './CreateModelModal'
import { EditModelModal } from './EditModelModal'
import { Button } from '@/shared/components/Button'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { Model } from '@/shared/types/api'
import { modelService } from '../services/modelService'

export function ModelList() {
    const { data: models, isLoading, error } = useModels()
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
    const [isEditModalOpen, setIsEditModalOpen] = useState(false)
    const [editingModel, setEditingModel] = useState<Model | null>(null)

    const handleModelCreated = async (nombre: string) => {
        // Después de crear, mostrar mensaje de éxito
        // El usuario puede abrir el navegador manualmente cuando quiera
        console.log(`✅ Modelo "${nombre}" creado exitosamente`)
        // No abrir navegador automáticamente para evitar errores
    }

    const handleOpenBrowser = async (modelo: string) => {
        try {
            await modelService.openBrowser(modelo)
        } catch (error) {
            console.error('Error abriendo navegador:', error)
            alert('Error al abrir el navegador. Por favor, intenta de nuevo.')
        }
    }

    const handleEdit = (model: Model) => {
        setEditingModel(model)
        setIsEditModalOpen(true)
    }

    const handleEditClose = () => {
        setIsEditModalOpen(false)
        setEditingModel(null)
    }

    const handleViewMetrics = (modelo: string) => {
        window.location.href = `/models/${modelo}/metrics`
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <p className="text-slate-400">
                    {isLoading ? 'Cargando...' : `${models?.length || 0} modelo${models?.length !== 1 ? 's' : ''} registrado${models?.length !== 1 ? 's' : ''}`}
                </p>
                <Button
                    onClick={() => setIsCreateModalOpen(true)}
                    size="sm"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    Crear Modelo
                </Button>
            </div>

            {error && !isLoading && (
                <div className="text-center py-4 mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <p className="text-red-400 text-sm font-semibold mb-2">
                        ⚠️ Error cargando modelos
                    </p>
                    <p className="text-red-300 text-xs mb-2">
                        {(error as Error).message}
                    </p>
                    {(error as Error).message?.includes('ECONNREFUSED') || (error as Error).message?.includes('Network Error') ? (
                        <p className="text-slate-400 text-xs mt-2">
                            Verifica que el backend esté corriendo en http://localhost:8000
                        </p>
                    ) : (
                        <p className="text-slate-400 text-xs mt-2">
                            Puedes crear un nuevo modelo usando el botón de arriba
                        </p>
                    )}
                </div>
            )}

            {isLoading ? (
                <div className="flex justify-center py-8">
                    <LoadingSpinner />
                </div>
            ) : (
                <>
                    {models && models.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {models.map((model) => (
                                <ModelCard 
                                    key={model.modelo} 
                                    model={model}
                                    onOpenBrowser={handleOpenBrowser}
                                    onEdit={handleEdit}
                                    onViewMetrics={handleViewMetrics}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-12">
                            <p className="text-slate-400 mb-4">No hay modelos registrados</p>
                            <Button onClick={() => setIsCreateModalOpen(true)} size="sm">
                                <Plus className="w-4 h-4 mr-2" />
                                Crear Primer Modelo
                            </Button>
                        </div>
                    )}
                </>
            )}

            <CreateModelModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onModelCreated={handleModelCreated}
            />

            {editingModel && (
                <EditModelModal
                    isOpen={isEditModalOpen}
                    onClose={handleEditClose}
                    model={editingModel}
                />
            )}
        </div>
    )
}
