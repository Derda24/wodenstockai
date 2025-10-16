import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'WODEN Stock AI - Intelligent Stock Management System',
  description: 'AI-powered stock management system with recipe-based inventory control, sales analytics, and intelligent recommendations.',
  icons: {
      icon: '/favicon.svg',
  shortcut: '/favicon.svg',
  apple: '/favicon.svg',
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
              <link rel="icon" href="/favicon.svg" />
      <link rel="apple-touch-icon" href="/favicon.svg" />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
