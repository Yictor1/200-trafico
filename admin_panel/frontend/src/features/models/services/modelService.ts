import { api } from '@/shared/lib/axios'
import { Model, ModelCreate, ModelUpdate } from '@/shared/types/api'

export const modelService = {
    async getAll(): Promise<Model[]> {
        const { data } = await api.get('/api/models')
        return data
    },

    async getOne(nombre: string): Promise<Model> {
        const { data } = await api.get(`/api/models/${nombre}`)
        return data
    },

    async create(model: ModelCreate): Promise<Model> {
        const formData = new FormData()
        formData.append('nombre', model.nombre)
        formData.append('telegram_user_id', model.telegram_user_id)
        formData.append('plataformas', model.plataformas)
        formData.append('hora_inicio', model.hora_inicio)
        formData.append('ventana_horas', model.ventana_horas.toString())
        formData.append('caracteristicas', JSON.stringify(model.caracteristicas))
        
        if (model.profile_photo instanceof File) {
            formData.append('profile_photo', model.profile_photo)
        }
        
        if (model.striphours_url) {
            formData.append('striphours_url', model.striphours_url)
        }

        const { data } = await api.post('/api/models', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
        return data
    },

    async update(nombre: string, model: ModelUpdate): Promise<Model> {
        const formData = new FormData()
        if (model.telegram_user_id) formData.append('telegram_user_id', model.telegram_user_id)
        if (model.plataformas) formData.append('plataformas', model.plataformas)
        if (model.hora_inicio) formData.append('hora_inicio', model.hora_inicio)
        if (model.ventana_horas !== undefined) formData.append('ventana_horas', model.ventana_horas.toString())
        if (model.caracteristicas) formData.append('caracteristicas', JSON.stringify(model.caracteristicas))
        if (model.striphours_url !== undefined) formData.append('striphours_url', model.striphours_url || '')
        
        if (model.profile_photo instanceof File) {
            formData.append('profile_photo', model.profile_photo)
        }

        const { data } = await api.put(`/api/models/${nombre}/editar`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
        return data
    },

    async delete(nombre: string): Promise<void> {
        await api.delete(`/api/models/${nombre}`)
    },

    async openBrowser(modelo: string): Promise<void> {
        await api.post(`/api/navegador/abrir/${modelo}`)
    },
}
