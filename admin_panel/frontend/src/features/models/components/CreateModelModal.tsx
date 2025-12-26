'use client'

import { useState, useRef } from 'react'
import { Modal } from '@/shared/components/Modal'
import { Input } from '@/shared/components/Input'
import { Button } from '@/shared/components/Button'
import { useCreateModel } from '../hooks/useModels'
import { ExternalLink, Upload, X } from 'lucide-react'

interface CreateModelModalProps {
    isOpen: boolean
    onClose: () => void
    onModelCreated?: (nombre: string) => void
}

export function CreateModelModal({ isOpen, onClose, onModelCreated }: CreateModelModalProps) {
    const createModel = useCreateModel()
    const fileInputRef = useRef<HTMLInputElement>(null)
    const [previewImage, setPreviewImage] = useState<string | null>(null)
    
    const [formData, setFormData] = useState({
        nombre: '',
        telegram_user_id: '',
        plataformas: 'kams,xxxfollow',
        hora_inicio: '12:00',
        ventana_horas: 5,
        profile_photo: null as File | null,
        striphours_url: '',
        caracteristicas: {
            tipo_cuerpo: 'Normal',
            tamano_pechos: 'Medianos',
            tamano_culo: 'Normal',
            color_cabello: 'Oscuro',
            color_cabello_otro: '',
            categoria: 'Teen',
            piercings: false,
            tatuajes: false,
        },
    })
    
    const [errors, setErrors] = useState<Record<string, string>>({})

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            // Validar que sea imagen
            if (!file.type.startsWith('image/')) {
                setErrors({ ...errors, profile_photo: 'Debe ser un archivo de imagen' })
                return
            }
            
            // Crear preview
            const reader = new FileReader()
            reader.onloadend = () => {
                setPreviewImage(reader.result as string)
            }
            reader.readAsDataURL(file)
            
            setFormData({ ...formData, profile_photo: file })
            setErrors({ ...errors, profile_photo: '' })
        }
    }

    const handleCropImage = () => {
        // TODO: Implementar crop 1:1 si es necesario
        // Por ahora solo validamos que la imagen existe
    }

    const validate = () => {
        const newErrors: Record<string, string> = {}

        if (!formData.nombre.trim()) {
            newErrors.nombre = 'El nombre es requerido'
        }

        if (!formData.telegram_user_id.trim()) {
            newErrors.telegram_user_id = 'El Telegram User ID es requerido'
        } else if (!/^\d+$/.test(formData.telegram_user_id.trim())) {
            newErrors.telegram_user_id = 'Debe ser un número (ej: 7206023342)'
        }

        if (!formData.plataformas.trim()) {
            newErrors.plataformas = 'Las plataformas son requeridas'
        }

        if (!formData.profile_photo) {
            newErrors.profile_photo = 'La foto de perfil es requerida'
        }

        if (!formData.caracteristicas.tipo_cuerpo) {
            newErrors.tipo_cuerpo = 'El tipo de cuerpo es requerido'
        }

        if (!formData.caracteristicas.tamano_pechos) {
            newErrors.tamano_pechos = 'El tamaño de pechos es requerido'
        }

        if (!formData.caracteristicas.tamano_culo) {
            newErrors.tamano_culo = 'El tamaño de culo es requerido'
        }

        if (!formData.caracteristicas.color_cabello) {
            newErrors.color_cabello = 'El color de cabello es requerido'
        }

        if (formData.caracteristicas.color_cabello === 'Otro' && !formData.caracteristicas.color_cabello_otro.trim()) {
            newErrors.color_cabello_otro = 'Especifica el color de cabello'
        }

        if (!formData.caracteristicas.categoria) {
            newErrors.categoria = 'La categoría es requerida'
        }

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!validate()) return

        try {
            const nombreNormalizado = formData.nombre.toLowerCase().replace(/\s+/g, '_')
            
            // Determinar color de cabello final
            const colorCabelloFinal = formData.caracteristicas.color_cabello === 'Otro' 
                ? formData.caracteristicas.color_cabello_otro 
                : formData.caracteristicas.color_cabello

            const result = await createModel.mutateAsync({
                nombre: nombreNormalizado,
                telegram_user_id: formData.telegram_user_id.trim(),
                plataformas: formData.plataformas.trim(),
                hora_inicio: formData.hora_inicio,
                ventana_horas: formData.ventana_horas,
                profile_photo: formData.profile_photo!,
                striphours_url: formData.striphours_url.trim() || undefined,
                caracteristicas: {
                    ...formData.caracteristicas,
                    color_cabello: colorCabelloFinal,
                },
            })

            console.log('✅ Modelo creado exitosamente:', result)

            // Reset form
            setFormData({
                nombre: '',
                telegram_user_id: '',
                plataformas: 'kams,xxxfollow',
                hora_inicio: '12:00',
                ventana_horas: 5,
                profile_photo: null,
                striphours_url: '',
                caracteristicas: {
                    tipo_cuerpo: 'Normal',
                    tamano_pechos: 'Medianos',
                    tamano_culo: 'Normal',
                    color_cabello: 'Oscuro',
                    color_cabello_otro: '',
                    categoria: 'Teen',
                    piercings: false,
                    tatuajes: false,
                },
            })
            setPreviewImage(null)
            setErrors({})
            
            // Llamar callback (sin abrir navegador automáticamente)
            if (onModelCreated) {
                onModelCreated(nombreNormalizado)
            }
            
            onClose()
        } catch (error: any) {
            console.error('Error completo al crear modelo:', error)
            console.error('Error response:', error.response)
            console.error('Error message:', error.message)
            
            const errorMessage = error.response?.data?.detail || error.message || 'Error creando modelo'
            setErrors({
                submit: errorMessage
            })
        }
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="✨ Crear Nuevo Modelo">
            <form onSubmit={handleSubmit} className="space-y-4 max-h-[80vh] overflow-y-auto">
                {/* Nombre */}
                <Input
                    label="Nombre de la modelo *"
                    placeholder="ej: maria"
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    error={errors.nombre}
                />

                {/* Foto de perfil */}
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                        Foto de perfil * (1:1)
                    </label>
                    <div className="flex items-center gap-4">
                        {previewImage ? (
                            <div className="relative">
                                <img
                                    src={previewImage}
                                    alt="Preview"
                                    className="w-24 h-24 rounded-full object-cover"
                                />
                                <button
                                    type="button"
                                    onClick={() => {
                                        setPreviewImage(null)
                                        setFormData({ ...formData, profile_photo: null })
                                        if (fileInputRef.current) fileInputRef.current.value = ''
                                    }}
                                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-white text-xs hover:bg-red-600"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        ) : (
                            <div className="w-24 h-24 rounded-full bg-slate-700 flex items-center justify-center">
                                <Upload className="w-8 h-8 text-slate-400" />
                            </div>
                        )}
                        <div>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleImageChange}
                                className="hidden"
                                id="profile-photo-input"
                            />
                            <Button
                                type="button"
                                variant="secondary"
                                size="sm"
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <Upload className="w-4 h-4 mr-2" />
                                Subir Foto
                            </Button>
                        </div>
                    </div>
                    {errors.profile_photo && (
                        <p className="text-red-400 text-xs mt-1">{errors.profile_photo}</p>
                    )}
                </div>

                {/* Telegram User ID */}
                <Input
                    label="Telegram User ID *"
                    placeholder="7206023342"
                    type="text"
                    value={formData.telegram_user_id}
                    onChange={(e) => setFormData({ ...formData, telegram_user_id: e.target.value })}
                    error={errors.telegram_user_id}
                    helperText="Número único del usuario de Telegram (ej: 7206023342). Puedes obtenerlo enviando /start al bot."
                />

                {/* Plataformas */}
                <Input
                    label="Plataformas *"
                    placeholder="kams,xxxfollow,myclub"
                    type="text"
                    value={formData.plataformas}
                    onChange={(e) => setFormData({ ...formData, plataformas: e.target.value })}
                    error={errors.plataformas}
                    helperText="Plataformas separadas por comas (ej: kams,xxxfollow,myclub). Estas son las plataformas donde se publicará el contenido."
                />

                {/* Striphours URL */}
                <Input
                    label="URL de Striphours (Opcional)"
                    placeholder="https://www.striphours.com/user/amberhudson"
                    type="url"
                    value={formData.striphours_url}
                    onChange={(e) => setFormData({ ...formData, striphours_url: e.target.value })}
                    helperText="URL completa del perfil de Striphours. Se usarán las métricas automáticamente."
                />

                {/* Hora de inicio */}
                <Input
                    label="Hora de inicio *"
                    type="time"
                    value={formData.hora_inicio}
                    onChange={(e) => setFormData({ ...formData, hora_inicio: e.target.value })}
                />

                {/* Ventana de horas */}
                <Input
                    label="Ventana de horas *"
                    type="number"
                    min="1"
                    max="24"
                    value={formData.ventana_horas}
                    onChange={(e) => setFormData({ ...formData, ventana_horas: parseInt(e.target.value) || 5 })}
                />

                {/* Características físicas */}
                <div className="border-t border-slate-700 pt-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Características Físicas *</h3>

                    {/* Tipo de cuerpo */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Tipo de cuerpo *
                        </label>
                        <select
                            value={formData.caracteristicas.tipo_cuerpo}
                            onChange={(e) => setFormData({
                                ...formData,
                                caracteristicas: { ...formData.caracteristicas, tipo_cuerpo: e.target.value }
                            })}
                            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="Delgada">Delgada</option>
                            <option value="Normal">Normal</option>
                            <option value="Curvy">Curvy</option>
                        </select>
                        {errors.tipo_cuerpo && (
                            <p className="text-red-400 text-xs mt-1">{errors.tipo_cuerpo}</p>
                        )}
                    </div>

                    {/* Tamaño de pechos */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Tamaño de pechos *
                        </label>
                        <select
                            value={formData.caracteristicas.tamano_pechos}
                            onChange={(e) => setFormData({
                                ...formData,
                                caracteristicas: { ...formData.caracteristicas, tamano_pechos: e.target.value }
                            })}
                            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="Pequeños">Pequeños</option>
                            <option value="Medianos">Medianos</option>
                            <option value="Grandes">Grandes</option>
                        </select>
                        {errors.tamano_pechos && (
                            <p className="text-red-400 text-xs mt-1">{errors.tamano_pechos}</p>
                        )}
                    </div>

                    {/* Tamaño de culo */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Tamaño de culo *
                        </label>
                        <select
                            value={formData.caracteristicas.tamano_culo}
                            onChange={(e) => setFormData({
                                ...formData,
                                caracteristicas: { ...formData.caracteristicas, tamano_culo: e.target.value }
                            })}
                            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="Pequeño">Pequeño</option>
                            <option value="Normal">Normal</option>
                            <option value="Grande">Grande</option>
                        </select>
                        {errors.tamano_culo && (
                            <p className="text-red-400 text-xs mt-1">{errors.tamano_culo}</p>
                        )}
                    </div>

                    {/* Color de cabello */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Color de cabello *
                        </label>
                        <select
                            value={formData.caracteristicas.color_cabello}
                            onChange={(e) => setFormData({
                                ...formData,
                                caracteristicas: { ...formData.caracteristicas, color_cabello: e.target.value }
                            })}
                            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 mb-2"
                        >
                            <option value="Claro">Claro</option>
                            <option value="Oscuro">Oscuro</option>
                            <option value="Rojo">Rojo</option>
                            <option value="Otro">Otro</option>
                        </select>
                        {formData.caracteristicas.color_cabello === 'Otro' && (
                            <Input
                                placeholder="Especifica el color"
                                value={formData.caracteristicas.color_cabello_otro}
                                onChange={(e) => setFormData({
                                    ...formData,
                                    caracteristicas: { ...formData.caracteristicas, color_cabello_otro: e.target.value }
                                })}
                                error={errors.color_cabello_otro}
                            />
                        )}
                        {errors.color_cabello && (
                            <p className="text-red-400 text-xs mt-1">{errors.color_cabello}</p>
                        )}
                    </div>

                    {/* Categoría */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Categoría *
                        </label>
                        <select
                            value={formData.caracteristicas.categoria}
                            onChange={(e) => setFormData({
                                ...formData,
                                caracteristicas: { ...formData.caracteristicas, categoria: e.target.value }
                            })}
                            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="Teen">Teen</option>
                            <option value="Milf">Milf</option>
                        </select>
                        {errors.categoria && (
                            <p className="text-red-400 text-xs mt-1">{errors.categoria}</p>
                        )}
                    </div>

                    {/* Piercings */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Piercings *
                        </label>
                        <div className="flex gap-4">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    name="piercings"
                                    checked={formData.caracteristicas.piercings === true}
                                    onChange={() => setFormData({
                                        ...formData,
                                        caracteristicas: { ...formData.caracteristicas, piercings: true }
                                    })}
                                    className="w-4 h-4 text-primary-500"
                                />
                                <span className="text-slate-300">SÍ</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    name="piercings"
                                    checked={formData.caracteristicas.piercings === false}
                                    onChange={() => setFormData({
                                        ...formData,
                                        caracteristicas: { ...formData.caracteristicas, piercings: false }
                                    })}
                                    className="w-4 h-4 text-primary-500"
                                />
                                <span className="text-slate-300">NO</span>
                            </label>
                        </div>
                    </div>

                    {/* Tatuajes */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Tatuajes *
                        </label>
                        <div className="flex gap-4">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    name="tatuajes"
                                    checked={formData.caracteristicas.tatuajes === true}
                                    onChange={() => setFormData({
                                        ...formData,
                                        caracteristicas: { ...formData.caracteristicas, tatuajes: true }
                                    })}
                                    className="w-4 h-4 text-primary-500"
                                />
                                <span className="text-slate-300">SÍ</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    name="tatuajes"
                                    checked={formData.caracteristicas.tatuajes === false}
                                    onChange={() => setFormData({
                                        ...formData,
                                        caracteristicas: { ...formData.caracteristicas, tatuajes: false }
                                    })}
                                    className="w-4 h-4 text-primary-500"
                                />
                                <span className="text-slate-300">NO</span>
                            </label>
                        </div>
                    </div>
                </div>

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
                        isLoading={createModel.isPending}
                    >
                        Crear Modelo
                    </Button>
                </div>
            </form>
        </Modal>
    )
}
