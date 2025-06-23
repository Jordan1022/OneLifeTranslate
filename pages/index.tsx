import { useState, useEffect, useRef } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { PlayIcon, StopIcon, SpeakerWaveIcon, ExclamationTriangleIcon, LockClosedIcon } from '@heroicons/react/24/solid'
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
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authToken, setAuthToken] = useState<string | null>(null)
  const [authError, setAuthError] = useState<string | null>(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [status, setStatus] = useState<StreamStatus | null>(null)
  const [captions, setCaptions] = useState<Caption[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  const eventSourceRef = useRef<EventSource | null>(null)
  const streamUrl = '/stream/playlist.m3u8'
  const maxRetries = 3

  // Authentication check on component mount
  useEffect(() => {
    const token = router.query.token as string
    if (router.isReady) {
      if (!token) {
        setAuthError('Access token required. Please use the official link.')
        return
      }

      // Validate token with backend
      validateToken(token)
    }
  }, [router.isReady, router.query.token])

  const validateToken = async (token: string) => {
    try {
      const response = await fetch('/api/validate-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      })

      if (response.ok) {
        setIsAuthenticated(true)
        setAuthToken(token)
        setAuthError(null)
      } else {
        setAuthError('Invalid access token. Please contact church staff for assistance.')
      }
    } catch (err) {
      setAuthError('Unable to verify access. Please check your connection and try again.')
    }
  }

  // Fetch status on component mount (only if authenticated)
  useEffect(() => {
    if (isAuthenticated) {
      fetchStatus()
      const interval = setInterval(fetchStatus, 5000) // Update every 5 seconds
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  // Set up SSE for captions (only if authenticated)
  useEffect(() => {
    if (isAuthenticated && isStreaming) {
      setupCaptionsStream()
    } else {
      cleanupCaptionsStream()
    }

    return () => cleanupCaptionsStream()
  }, [isAuthenticated, isStreaming])

  const fetchStatus = async () => {
    if (!authToken) return

    try {
      const response = await fetch('/api/status', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setStatus(data)
      setIsStreaming(data.status === 'running')
      setRetryCount(0) // Reset retry count on success
    } catch (err) {
      console.error('Failed to fetch status:', err)
      if (retryCount < maxRetries) {
        setRetryCount(prev => prev + 1)
        setTimeout(fetchStatus, 2000) // Retry after 2 seconds
      }
    }
  }

  const setupCaptionsStream = () => {
    if (!authToken) return

    cleanupCaptionsStream()

    eventSourceRef.current = new EventSource(`/api/captions?token=${authToken}`)

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

      // Attempt to reconnect after a delay
      setTimeout(() => {
        if (isStreaming) {
          setupCaptionsStream()
        }
      }, 3000)
    }
  }

  const cleanupCaptionsStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
  }

  const startStream = async () => {
    if (!authToken) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/start', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      const data = await response.json()
      setIsStreaming(true)
      setCaptions([]) // Clear previous captions
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Network error starting stream'
      setError(errorMessage)
      console.error('Start stream error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const stopStream = async () => {
    if (!authToken) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/stop', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      setIsStreaming(false)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Network error stopping stream'
      setError(errorMessage)
      console.error('Stop stream error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // Render access denied screen if not authenticated
  if (!isAuthenticated) {
    return (
      <>
        <Head>
          <title>OneLife Translation - Access Required</title>
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
          <div className="max-w-md w-full mx-4">
            <div className="bg-white rounded-2xl shadow-lg border border-slate-200/50 p-8 text-center">
              <div className="mb-6">
                <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                  <LockClosedIcon className="w-8 h-8 text-red-600" />
                </div>
                <h1 className="text-2xl font-semibold text-slate-900 mb-2">
                  Access Required
                </h1>
                <p className="text-slate-600">
                  {authError || 'Validating access...'}
                </p>
              </div>

              {authError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
                  <p className="font-medium mb-1">Unable to Access Translation Service</p>
                  <p>Please contact church staff for assistance or ensure you're using the official link.</p>
                </div>
              )}

              <div className="mt-6 pt-6 border-t border-slate-200">
                <div className="flex items-center justify-center space-x-2 text-sm text-slate-500">
                  <SpeakerWaveIcon className="w-4 h-4" />
                  <span>OneLife Church Spanish Translation</span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </>
    )
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

              <div className="flex items-center space-x-4">
                {retryCount > 0 && retryCount < maxRetries && (
                  <div className="text-xs text-amber-600 flex items-center space-x-1">
                    <ExclamationTriangleIcon className="w-4 h-4" />
                    <span>Reconnecting... ({retryCount}/{maxRetries})</span>
                  </div>
                )}
                <StatusIndicator status={status} />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">

            {/* Audio Player Section */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200/50 p-6 lg:p-8">
                <div className="text-center mb-6 lg:mb-8">
                  <h2 className="text-xl lg:text-2xl font-light text-slate-900 mb-2">
                    Spanish Audio Stream
                  </h2>
                  <p className="text-slate-600 text-sm lg:text-base">
                    Real-time translation from English service
                  </p>
                </div>

                {/* Control Button */}
                <div className="flex justify-center mb-6 lg:mb-8">
                  <button
                    onClick={isStreaming ? stopStream : startStream}
                    disabled={isLoading}
                    className={`
                      relative inline-flex items-center px-6 lg:px-8 py-3 lg:py-4 rounded-full font-medium
                      transition-all duration-200 transform hover:scale-105 focus:outline-none
                      focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:transform-none
                      text-sm lg:text-base
                      ${isStreaming
                        ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/25'
                        : 'bg-primary-600 hover:bg-primary-700 text-white shadow-lg shadow-primary-500/25'
                      }
                    `}
                  >
                    {isLoading ? (
                      <div className="w-5 h-5 lg:w-6 lg:h-6 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2 lg:mr-3" />
                    ) : (
                      <>
                        {isStreaming ? (
                          <StopIcon className="w-5 h-5 lg:w-6 lg:h-6 mr-2 lg:mr-3" />
                        ) : (
                          <PlayIcon className="w-5 h-5 lg:w-6 lg:h-6 mr-2 lg:mr-3" />
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
                    <div className="flex items-center space-x-2">
                      <ExclamationTriangleIcon className="w-5 h-5 text-red-500 flex-shrink-0" />
                      <p className="text-red-700 text-sm">{error}</p>
                    </div>
                    <button
                      onClick={() => setError(null)}
                      className="mt-2 text-xs text-red-600 hover:text-red-800"
                    >
                      Dismiss
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Captions Section */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200/50 p-4 lg:p-6">
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 mt-6 lg:mt-8">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-4 lg:p-6 text-center">
              <div className="text-xl lg:text-2xl font-semibold text-primary-600 mb-2">
                {status?.captions_count || 0}
              </div>
              <div className="text-xs lg:text-sm text-slate-600">
                Translations Processed
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-4 lg:p-6 text-center">
              <div className="text-xl lg:text-2xl font-semibold text-primary-600 mb-2">
                {status?.connected_clients || 0}
              </div>
              <div className="text-xs lg:text-sm text-slate-600">
                Connected Clients
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200/50 p-4 lg:p-6 text-center">
              <div className="text-xl lg:text-2xl font-semibold text-primary-600 mb-2">
                2-3s
              </div>
              <div className="text-xs lg:text-sm text-slate-600">
                Average Latency
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}