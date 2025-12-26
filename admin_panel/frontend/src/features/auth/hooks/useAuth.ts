import { useMutation, useQuery } from '@tanstack/react-query'
import { authService } from '../services/authService'

export function useStartAuth() {
    return useMutation({
        mutationFn: ({ modelo, plataforma, url }: { modelo: string; plataforma: string; url: string }) =>
            authService.startAuth(modelo, plataforma, url),
    })
}

export function useAuthStatus(sessionId: string | null) {
    return useQuery({
        queryKey: ['auth-status', sessionId],
        queryFn: () => authService.getStatus(sessionId!),
        enabled: !!sessionId,
        refetchInterval: 2000, // Poll cada 2 segundos
    })
}
