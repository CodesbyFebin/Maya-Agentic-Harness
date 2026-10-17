import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'MAYA Agentic Harness',
  description: 'Local-first personal AI command center and agentic harness. Systems that prove what happened.',
  openGraph: {
    title: 'MAYA Agentic Harness',
    description: 'JARVIS-style dashboard + agent runtime for OpenJarvis.',
    images: ['/og.png'],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MAYA Agentic Harness',
    description: 'Local-first AI command center that proves what happened.',
    images: ['/og.png'],
  },
  icons: {
    icon: '/favicon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
