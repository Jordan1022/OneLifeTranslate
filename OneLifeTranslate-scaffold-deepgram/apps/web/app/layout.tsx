import './globals.css'
import type { ReactNode } from 'react'

export const metadata = {
  title: 'OneLife Translate',
  description: 'Real-time captions and audio (EN → ES)',
  manifest: '/manifest.json',
  themeColor: '#0a0a0a'
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}