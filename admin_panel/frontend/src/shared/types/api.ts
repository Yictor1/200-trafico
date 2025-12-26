export interface Model {
    modelo: string
    telegram_user_id?: string
    telegram_username?: string  // Mantener para compatibilidad/display
    plataformas: string
    hora_inicio: string
    ventana_horas: number
    profile_photo?: string
    caracteristicas?: {
        tipo_cuerpo?: string
        tamano_pechos?: string
        tamano_culo?: string
        color_cabello?: string
        categoria?: string
        piercings?: boolean
        tatuajes?: boolean
    }
    striphours_url?: string
    striphours_username?: string
}

export interface ModelCreate {
    nombre: string
    telegram_user_id: string
    plataformas: string
    hora_inicio: string
    ventana_horas: number
    profile_photo?: string | File
    striphours_url?: string
    caracteristicas: {
        tipo_cuerpo: string
        tamano_pechos: string
        tamano_culo: string
        color_cabello: string
        categoria: string
        piercings: boolean
        tatuajes: boolean
    }
}

export interface ModelUpdate {
    telegram_user_id?: string
    plataformas?: string
    hora_inicio?: string
    ventana_horas?: number
    profile_photo?: string | File
    striphours_url?: string
    caracteristicas?: {
        tipo_cuerpo?: string
        tamano_pechos?: string
        tamano_culo?: string
        color_cabello?: string
        categoria?: string
        piercings?: boolean
        tatuajes?: boolean
    }
}

export interface Platform {
    nombre: string
    url: string
    has_worker: boolean
}

export interface Worker {
    nombre: string
    path: string
    size: number
    lines: number
}

export interface WorkerCode {
    nombre: string
    code: string
}

export interface CaptureSession {
    session_id: string
    status: 'capturing' | 'completed' | 'failed'
    message: string
    flow_data?: any
}
