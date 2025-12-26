import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'Trafico Admin Panel',
    description: 'Panel de administración para gestión de modelos y plataformas',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="es" className="dark">
            <body className={`${inter.className} antialiased`}>
                <Providers>
                    {children}
                </Providers>
            </body>
        </html>
    )
}
