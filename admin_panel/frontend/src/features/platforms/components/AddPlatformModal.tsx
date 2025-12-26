'use client'

import { useState } from 'react'
import { Modal } from '@/shared/components/Modal'
import { Input } from '@/shared/components/Input'
import { Button } from '@/shared/components/Button'
import { useCreatePlatform } from '../hooks/usePlatforms'
import { AlertCircle } from 'lucide-react'

interface AddPlatformModalProps {
    isOpen: boolean
    onClose: () => void
}

export function AddPlatformModal({ isOpen, onClose }: AddPlatformModalProps) {
    const createPlatform = useCreatePlatform()
    const [formData, setFormData] = useState({
        nombre: '',
        url: '',
    })
    const [errors, setErrors] = useState<Record<string, string>>({})

    const validate = () => {
        const newErrors: Record<string, string> = {}

        if (!formData.nombre.trim()) {
            newErrors.nombre = 'El nombre es requerido'
        }

        if (!formData.url.trim()) {
            newErrors.url = 'La URL es requerida'
        } else if (!formData.url.startsWith('http')) {
            newErrors.url = 'La URL debe comenzar con http:// o https://'
        }

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!validate()) return

        try {
            const nombreNormalizado = formData.nombre.toLowerCase().replace(/\s+/g, '_')

            await createPlatform.mutateAsync({
                nombre: nombreNormalizado,
                url: formData.url,
            })

            // Iniciar captura de network flow
            // Esto abrirá el navegador para capturar el flujo de publicación
            const captureResponse = await fetch('http://localhost:8000/api/capture/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    platform_name: nombreNormalizado,
                    platform_url: formData.url,
                    modelo: 'demo' // Modelo de demostración para la captura
                })
            })

            if (captureResponse.ok) {
                const captureData = await captureResponse.json()
                alert(`✅ Plataforma creada!\n\n🌐 Se abrió el navegador para capturar el flujo.\n\nInstrucciones:\n1. Haz login en la plataforma\n2. Sube un video de prueba\n3. Completa todo el proceso de publicación\n4. El navegador se cerrará automáticamente\n5. Se generará el worker en workers/${nombreNormalizado}.js`)
            }

            // Reset form
            setFormData({ nombre: '', url: '' })
            setErrors({})
            onClose()
        } catch (error: any) {
            setErrors({
                submit: error.response?.data?.detail || error.message || 'Error agregando plataforma'
            })
        }
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="🌐 Agregar Plataforma">
            <div className="mb-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <div className="flex gap-3">
                    <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-blue-300">
                        <p className="font-semibold mb-1">Próximo paso: Captura de credenciales</p>
                        <p className="text-blue-400">
                            Después de agregar la plataforma, se abrirá un navegador para que hagas login manualmente.
                            El sistema capturará el flujo de autenticación y generará un worker automáticamente.
                        </p>
                    </div>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                    label="Nombre de la Plataforma"
                    placeholder="ej: onlyfans"
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    error={errors.nombre}
                />

                <Input
                    label="URL de Login"
                    placeholder="https://example.com/login"
                    value={formData.url}
                    onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                    error={errors.url}
                    helperText="URL donde se realiza el login de la plataforma"
                />

                {errors.submit && (
                    <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                        <p className="text-red-400 text-sm">{errors.submit}</p>
                    </div>
                )}

                <div className="flex gap-3 pt-4">
                    <Button
                        type="button"
                        variant="secondary"
                        onClick={onClose}
                        className="flex-1"
                    >
                        Cancelar
                    </Button>
                    <Button
                        type="submit"
                        className="flex-1"
                        isLoading={createPlatform.isPending}
                    >
                        Continuar a Captura
                    </Button>
                </div>
            </form>
        </Modal>
    )
}
