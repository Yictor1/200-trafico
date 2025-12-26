'use client'

import { useParams } from 'next/navigation'
import { MetricsDashboard } from '@/features/kpi/components/MetricsDashboard'

export default function ModelMetricsPage() {
    const params = useParams()
    const modelo = params.modelo as string

    if (!modelo) {
        return (
            <div className="glass rounded-xl p-6">
                <p className="text-red-400">Modelo no especificado</p>
            </div>
        )
    }

    return (
        <div className="container mx-auto px-6 py-8">
            <MetricsDashboard modelo={modelo} />
        </div>
    )
}



