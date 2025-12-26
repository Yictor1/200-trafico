import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { workerService } from '../services/workerService'

export function useWorkers() {
    return useQuery({
        queryKey: ['workers'],
        queryFn: workerService.getAll,
    })
}

export function useWorkerCode(nombre: string) {
    return useQuery({
        queryKey: ['worker', nombre],
        queryFn: () => workerService.getCode(nombre),
        enabled: !!nombre,
    })
}

export function useUpdateWorker() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ nombre, code }: { nombre: string; code: string }) =>
            workerService.update(nombre, code),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['workers'] })
        },
    })
}

export function useDeleteWorker() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (nombre: string) => workerService.delete(nombre),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['workers'] })
        },
    })
}
