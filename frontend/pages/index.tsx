import { useState, useEffect, useRef } from 'react'
import Head from 'next/head'
import { PlayIcon, StopIcon, SpeakerWaveIcon } from '@heroicons/react/24/solid'
import AudioPlayer from '../components/AudioPlayer'
import CaptionDisplay from '../components/CaptionDisplay'
import StatusIndicator from '../components/StatusIndicator'

interface StreamStatus {
  status: 'not_initialized' | 'stopped' | 'running'
  captions_count: number
  connected_clients: number
  stream_start_time?: number
}

interface Caption {
  timestamp: number
  text: string
  language: string
}

export default function Home() {
  const [isStreaming, setIsStreaming] = useState(false)
  const [status, setStatus] = useState<StreamStatus | null>(null)
  const [captions, setCaptions] = useState<Caption[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const eventSourceRef = useRef<EventSource | null>(null)
  const streamUrl = '/stream/playlist.m3u8'

  // Fetch status on component mount
  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  // Set up SSE for captions
  useEffect(() => {
    if (isStreaming) {
      setupCaptionsStream()
    } else {
      cleanupCaptionsStream()
    }
    
    return () => cleanupCaptionsStream()
  }, [isStreaming])

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/status')
      const data = await response.json()
      setStatus(data)
      setIsStreaming(data.status === 'running')
    } catch (err) {
      console.error('Failed to fetch status:', err)
    }
  }

  const setupCaptionsStream = () => {
    cleanupCaptionsStream()
    
    eventSourceRef.current = new EventSource('/api/captions')
    
    eventSourceRef.current.onmessage = (event) => {
      try {
        const caption: Caption = JSON.parse(event.data)
        setCaptions(prev => [...prev.slice(-10), caption]) // Keep last 10 captions
      } catch (err) {
        console.error('Error parsing caption:', err)
      }
    }
    
    eventSourceRef.current.onerror = (err) => {
      console.error('SSE error:', err)
      setError('Connection to captions stream lost')
    }
  }

  const cleanupCaptionsStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
  }

  const startStream = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/start', { method: 'POST' })
      const data = await response.json()
      
      if (response.ok) {
        setIsStreaming(true)
        setCaptions([]) // Clear previous captions
      } else {
        setError(data.detail || 'Failed to start stream')
      }
    } catch (err) {
      setError('Network error starting stream')
    } finally {
      setIsLoading(false)
    }
  }

  const stopStream = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/stop', { method: 'POST' })
      
      if (response.ok) {
        setIsStreaming(false)
      } else {
        setError('Failed to stop stream')
      }
    } catch (err) {
      setError('Network error stopping stream')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <Head>
        <title>OneLife Translation Stream</title>
        <meta name="description" content="Real-time English to Spanish translation for church services" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200/50 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-3">
                <SpeakerWaveIcon className="h-8 w-8 text-primary-600" />
                <div>
                  <h1 className="text-xl font-semibold text-slate-900">
                    OneLife Translation
                  </h1>
                  <p className="text-sm text-slate-500">
                    English → Spanish Stream
                  </p>
                </div>
              </div>
              
              <StatusIndicator status={status} />
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Audio Player Section */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200/50 p-8">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-light text-slate-900 mb-2">
                    Spanish Audio Stream
                  </h2>
                  <p className="text-slate-600">
                    Real-time translation from English service
                  </p>
                </div>

                {/* Control Button */}
                <div className="flex justify-center mb-8">
                  <button
                    onClick={isStreaming ? stopStream : startStream}
                    disabled={isLoading}
                    className={`
                      relative inline-flex items-center px-8 py-4 rounded-full font-medium
                      transition-all duration-200 transform hover:scale-105 focus:outline-none
                      focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:transform-none
                      ${isStreaming 
                        ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/25' 
                        : 'bg-primary-600 hover:bg-primary-700 text-white shadow-lg shadow-primary-500/25'
                      }
                    `}
                  >
                    {isLoading ? (
                      <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin mr-3" />
                    ) : (
                      <>
                        {isStreaming ? (
                          <StopIcon className="w-6 h-6 mr-3" />
                        ) : (
                          <PlayIcon className="w-6 h-6 mr-3" />
                        )}
                      </>
                    )}
                    {isStreaming ? 'Stop Stream' : 'Start Stream'}
                  </button>
                </div>

                {/* Audio Player */}
                <AudioPlayer 
                  streamUrl={streamUrl} 
                  isActive={isStreaming}
                />

                {/* Error Display */}
                {error && (
                  <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-700 text-sm">{error}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Captions Section */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200/50 p-6">
                <h3 className="text-lg font-medium text-slate-900 mb-4">
                  Live Captions
                </h3>
                
                <CaptionDisplay 
                  captions={captions}
                  isActive={isStreaming}
                />
              </div>
            </div>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-6 text-center">
              <div className="text-2xl font-semibold text-primary-600 mb-2">
                {status?.captions_count || 0}
              </div>
              <div className="text-sm text-slate-600">
                Translations Processed
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-6 text-center">
              <div className="text-2xl font-semibold text-primary-600 mb-2">
                {status?.connected_clients || 0}
              </div>
              <div className="text-sm text-slate-600">
                Connected Clients
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-6 text-center">
              <div className="text-2xl font-semibold text-primary-600 mb-2">
                2-3s
              </div>
              <div className="text-sm text-slate-600">
                Average Latency
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}