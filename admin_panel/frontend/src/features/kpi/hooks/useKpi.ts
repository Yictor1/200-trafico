import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { kpiService, MetricsResponse, SyncResponse } from '../services/kpiService'

export function useModelMetrics(
    modelo: string,
    startDate?: string,
    endDate?: string,
    days: number = 30
) {
    return useQuery({
        queryKey: ['kpi', modelo, startDate, endDate, days],
        queryFn: () => kpiService.getMetrics(modelo, startDate, endDate, days),
        enabled: !!modelo,
        retry: 1,
        refetchOnWindowFocus: false,
        staleTime: 60000, // 1 minuto
    })
}

export function useSyncMetrics() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ modelo, days }: { modelo: string; days?: number }) =>
            kpiService.syncMetrics(modelo, days),
        onSuccess: (data, variables) => {
            // Invalidar TODAS las queries de métricas para este modelo (sin importar parámetros)
            queryClient.invalidateQueries({ queryKey: ['kpi', variables.modelo] })
            // También forzar refetch inmediato
            queryClient.refetchQueries({ queryKey: ['kpi', variables.modelo] })
        },
    })
}



