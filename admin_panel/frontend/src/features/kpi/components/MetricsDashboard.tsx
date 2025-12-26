'use client'

import { useState, useMemo } from 'react'
import { ArrowLeft, RefreshCw, Calendar } from 'lucide-react'
import { Button } from '@/shared/components/Button'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { useModelMetrics, useSyncMetrics } from '../hooks/useKpi'
import { DailyMetric } from '../services/kpiService'
import Link from 'next/link'

interface MetricsDashboardProps {
    modelo: string
}

export function MetricsDashboard({ modelo }: MetricsDashboardProps) {
    const [startDate, setStartDate] = useState<string>('')
    const [endDate, setEndDate] = useState<string>('')
    const [days, setDays] = useState<number>(30)

    // Calcular fechas por defecto (usar UTC para coincidir con el backend)
    const defaultEndDate = useMemo(() => {
        // Usar UTC para coincidir con la API de Striphours
        const today = new Date()
        const utcDate = new Date(Date.UTC(
            today.getUTCFullYear(),
            today.getUTCMonth(),
            today.getUTCDate()
        ))
        return utcDate.toISOString().split('T')[0]
    }, [])

    const defaultStartDate = useMemo(() => {
        // Calcular desde hoy UTC hacia atrás 29 días
        const today = new Date()
        const utcDate = new Date(Date.UTC(
            today.getUTCFullYear(),
            today.getUTCMonth(),
            today.getUTCDate()
        ))
        utcDate.setUTCDate(utcDate.getUTCDate() - 29)
        return utcDate.toISOString().split('T')[0]
    }, [])

    const finalStartDate = startDate || defaultStartDate
    const finalEndDate = endDate || defaultEndDate

    const { data, isLoading, error, refetch } = useModelMetrics(
        modelo,
        finalStartDate,
        finalEndDate,
        days
    )

    const syncMetrics = useSyncMetrics()

    const handleSync = async () => {
        try {
            await syncMetrics.mutateAsync({ modelo })
            // Refetch forzado después de sincronizar
            await refetch()
        } catch (error) {
            console.error('Error sincronizando:', error)
        }
    }

    const stats = useMemo(() => {
        if (!data?.daily_metrics || data.daily_metrics.length === 0) {
            return null
        }

        const metrics = data.daily_metrics
        const totalGrowth = metrics.reduce((sum, m) => sum + m.growth, 0)
        const avgRank = Math.round(
            metrics.reduce((sum, m) => sum + m.avg_rank, 0) / metrics.length
        )
        const bestRankEver = Math.min(...metrics.map((m) => m.best_rank))
        const maxViewers = Math.max(...metrics.map((m) => m.most_viewers))

        return {
            totalGrowth,
            avgRank,
            bestRankEver,
            maxViewers,
        }
    }, [data])

    if (isLoading) {
        return (
            <div className="flex justify-center items-center min-h-[400px]">
                <LoadingSpinner />
            </div>
        )
    }

    if (error) {
        return (
            <div className="glass rounded-xl p-6">
                <div className="text-center">
                    <p className="text-red-400 mb-4">
                        Error cargando métricas: {(error as Error).message}
                    </p>
                    <Button onClick={() => refetch()} variant="secondary">
                        Reintentar
                    </Button>
                </div>
            </div>
        )
    }

    if (!data || data.daily_metrics.length === 0) {
        return (
            <div className="glass rounded-xl p-6">
                <div className="text-center">
                    <p className="text-slate-400 mb-4">
                        No hay métricas disponibles para este modelo
                    </p>
                    <Button onClick={handleSync} isLoading={syncMetrics.isPending}>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Sincronizar Métricas
                    </Button>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/">
                        <Button variant="secondary" size="sm">
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Volver
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-white">{modelo}</h1>
                        <p className="text-slate-400 text-sm">
                            Métricas de Striphours (fechas en UTC)
                        </p>
                        {data?.last_sync && (
                            <p className="text-slate-500 text-xs mt-1">
                                Última sincronización: {new Date(data.last_sync + 'T00:00:00Z').toLocaleDateString('es-ES', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric',
                                    timeZone: 'UTC'
                                })} UTC
                            </p>
                        )}
                    </div>
                </div>
                <Button
                    onClick={handleSync}
                    variant="secondary"
                    isLoading={syncMetrics.isPending}
                >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Sincronizar
                </Button>
            </div>

            {/* Stats Grid */}
            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="glass rounded-xl p-6">
                        <div className="text-sm text-slate-400 mb-2 uppercase tracking-wide">
                            Mejor Rank Global
                        </div>
                        <div className="text-3xl font-bold text-white">{stats.bestRankEver}</div>
                        <div className="text-xs text-slate-500 mt-2">En el período analizado</div>
                    </div>
                    <div className="glass rounded-xl p-6">
                        <div className="text-sm text-slate-400 mb-2 uppercase tracking-wide">
                            Rank Promedio
                        </div>
                        <div className="text-3xl font-bold text-white">{stats.avgRank}</div>
                        <div className="text-xs text-slate-500 mt-2">
                            Últimos {data.total_days} días
                        </div>
                    </div>
                    <div className="glass rounded-xl p-6">
                        <div className="text-sm text-slate-400 mb-2 uppercase tracking-wide">
                            Crecimiento Total
                        </div>
                        <div
                            className={`text-3xl font-bold ${
                                stats.totalGrowth > 0 ? 'text-green-400' : 'text-red-400'
                            }`}
                        >
                            {stats.totalGrowth > 0 ? '+' : ''}
                            {stats.totalGrowth}
                        </div>
                        <div className="text-xs text-slate-500 mt-2">Nuevos seguidores</div>
                    </div>
                    <div className="glass rounded-xl p-6">
                        <div className="text-sm text-slate-400 mb-2 uppercase tracking-wide">
                            Viewers Máximos
                        </div>
                        <div className="text-3xl font-bold text-white">{stats.maxViewers}</div>
                        <div className="text-xs text-slate-500 mt-2">Pico de audiencia</div>
                    </div>
                </div>
            )}

            {/* Date Range Controls */}
            <div className="glass rounded-xl p-4">
                <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <label className="text-sm text-slate-300">Desde:</label>
                        <input
                            type="date"
                            value={startDate || defaultStartDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <label className="text-sm text-slate-300">Hasta:</label>
                        <input
                            type="date"
                            value={endDate || defaultEndDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <label className="text-sm text-slate-300">Días:</label>
                        <select
                            value={days}
                            onChange={(e) => {
                                setDays(Number(e.target.value))
                                // Usar UTC para coincidir con el backend
                                const today = new Date()
                                const endUtc = new Date(Date.UTC(
                                    today.getUTCFullYear(),
                                    today.getUTCMonth(),
                                    today.getUTCDate()
                                ))
                                const startUtc = new Date(endUtc)
                                startUtc.setUTCDate(startUtc.getUTCDate() - (Number(e.target.value) - 1))
                                setEndDate(endUtc.toISOString().split('T')[0])
                                setStartDate(startUtc.toISOString().split('T')[0])
                            }}
                            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value={7}>7 días</option>
                            <option value={14}>14 días</option>
                            <option value={30}>30 días</option>
                            <option value={60}>60 días</option>
                        </select>
                    </div>
                    {data.last_sync && (
                        <div className="text-xs text-slate-500 ml-auto">
                            Última sincronización: {new Date(data.last_sync).toLocaleString()}
                        </div>
                    )}
                </div>
            </div>

            {/* Table */}
            <div className="glass rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-slate-800/50 border-b border-slate-700">
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Fecha
                                </th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Best Rank
                                </th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Avg. Rank
                                </th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Best Gender Rank
                                </th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Avg. Gender Rank
                                </th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Most Viewers
                                </th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Avg. Viewers
                                </th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Followers Inicio
                                </th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Followers Final
                                </th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                                    Crecimiento
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.daily_metrics.map((metric: DailyMetric) => (
                                <tr
                                    key={metric.fecha}
                                    className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors"
                                >
                                    <td className="px-6 py-4 text-sm text-white font-medium">
                                        {(() => {
                                            // Interpretar la fecha como UTC para evitar desfases de zona horaria
                                            const [year, month, day] = metric.fecha.split('-').map(Number)
                                            const date = new Date(Date.UTC(year, month - 1, day))
                                            return date.toLocaleDateString('es-ES', {
                                                weekday: 'short',
                                                year: 'numeric',
                                                month: 'short',
                                                day: 'numeric',
                                                timeZone: 'UTC'
                                            })
                                        })()}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        {metric.best_rank}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        {metric.avg_rank}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        {metric.best_gender_rank}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        {metric.avg_gender_rank}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        {metric.most_viewers}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        {metric.avg_viewers.toFixed(1)}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        {metric.starting_followers}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        {metric.ending_followers}
                                    </td>
                                    <td
                                        className={`px-6 py-4 text-sm font-semibold ${
                                            metric.growth > 0
                                                ? 'text-green-400'
                                                : metric.growth < 0
                                                  ? 'text-red-400'
                                                  : 'text-slate-300'
                                        }`}
                                    >
                                        {metric.growth > 0 ? '+' : ''}
                                        {metric.growth}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}



