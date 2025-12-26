import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { modelService } from '../services/modelService'
import { ModelCreate, ModelUpdate } from '@/shared/types/api'

export function useModels() {
    return useQuery({
        queryKey: ['models'],
        queryFn: modelService.getAll,
        retry: 1,
        refetchOnWindowFocus: false,
        staleTime: 30000, // 30 segundos
        gcTime: 60000, // 1 minuto (antes cacheTime)
    })
}

export function useCreateModel() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (model: ModelCreate) => modelService.create(model),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['models'] })
        },
    })
}

export function useUpdateModel() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ nombre, data }: { nombre: string; data: ModelUpdate }) => 
            modelService.update(nombre, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['models'] })
        },
    })
}

export function useDeleteModel() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (nombre: string) => modelService.delete(nombre),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['models'] })
        },
    })
}
