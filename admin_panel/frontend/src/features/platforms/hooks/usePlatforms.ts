import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { platformService } from '../services/platformService'

export function usePlatforms() {
    return useQuery({
        queryKey: ['platforms'],
        queryFn: platformService.getAll,
    })
}

export function useCreatePlatform() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (platform: { nombre: string; url: string }) => platformService.create(platform),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['platforms'] })
        },
    })
}
