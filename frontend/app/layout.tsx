import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'WODEN Stock AI - Intelligent Stock Management System',
  description: 'AI-powered stock management system with recipe-based inventory control, sales analytics, and intelligent recommendations.',
  icons: {
    icon: '/AI-LOGO.png',
    shortcut: '/AI-LOGO.png',
    apple: '/AI-LOGO.png',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/AI-LOGO.png" />
        <link rel="apple-touch-icon" href="/AI-LOGO.png" />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
