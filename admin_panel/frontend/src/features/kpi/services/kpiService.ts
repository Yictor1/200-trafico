import { api } from '@/shared/lib/axios'

export interface DailyMetric {
    fecha: string
    best_rank: number
    avg_rank: number
    best_gender_rank: number
    avg_gender_rank: number
    most_viewers: number
    avg_viewers: number
    starting_followers: number
    ending_followers: number
    growth: number
    total_segments: number
}

export interface MetricsResponse {
    modelo: string
    total_days: number
    date_range: {
        start: string
        end: string
    }
    daily_metrics: DailyMetric[]
    last_sync: string | null
}

export interface SyncResponse {
    success: boolean
    message: string
    is_first_time?: boolean
    synced_date?: string
}

export const kpiService = {
    async getMetrics(
        modelo: string,
        startDate?: string,
        endDate?: string,
        days: number = 30
    ): Promise<MetricsResponse> {
        const params = new URLSearchParams()
        if (startDate) params.append('start_date', startDate)
        if (endDate) params.append('end_date', endDate)
        params.append('days', days.toString())

        const response = await api.get<MetricsResponse>(
            `/api/kpi/${modelo}?${params.toString()}`
        )
        return response.data
    },

    async syncMetrics(modelo: string, days: number = 30): Promise<SyncResponse> {
        const response = await api.post<SyncResponse>(
            `/api/kpi/${modelo}/sync`,
            { days }
        )
        return response.data
    },
}

