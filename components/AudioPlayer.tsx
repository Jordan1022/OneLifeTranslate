import { useEffect, useRef, useState } from 'react'
import { SpeakerWaveIcon, SpeakerXMarkIcon } from '@heroicons/react/24/outline'
import Hls from 'hls.js'

interface AudioPlayerProps {
  streamUrl: string
  isActive: boolean
}

export default function AudioPlayer({ streamUrl, isActive }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const hlsRef = useRef<Hls | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState(0.8)
  const [isMuted, setIsMuted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Initialize HLS
  useEffect(() => {
    if (!audioRef.current) return

    const audio = audioRef.current

    const handleLoadStart = () => setIsLoading(true)
    const handleCanPlay = () => {
      setIsLoading(false)
      setError(null)
    }
    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleError = (e: Event) => {
      setIsLoading(false)
      setError('Error loading audio stream')
      console.error('Audio error:', e)
    }

    audio.addEventListener('loadstart', handleLoadStart)
    audio.addEventListener('canplay', handleCanPlay)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('error', handleError)

    return () => {
      audio.removeEventListener('loadstart', handleLoadStart)
      audio.removeEventListener('canplay', handleCanPlay)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('error', handleError)
    }
  }, [])

  // Handle HLS setup and cleanup
  useEffect(() => {
    if (!audioRef.current) return

    const audio = audioRef.current

    if (isActive) {
      setIsLoading(true)
      setError(null)

      if (Hls.isSupported()) {
        // Use HLS.js for browsers that support it
        if (hlsRef.current) {
          hlsRef.current.destroy()
        }

        const hls = new Hls({
          enableWorker: true,
          lowLatencyMode: true,
          backBufferLength: 90
        })

        hlsRef.current = hls

        hls.loadSource(streamUrl)
        hls.attachMedia(audio)

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          console.log('HLS manifest parsed, trying to play')
          audio.play().catch(err => {
            console.error('Auto-play failed:', err)
            setError('Click play to start audio (browser blocked auto-play)')
          })
        })

        hls.on(Hls.Events.ERROR, (event, data) => {
          console.error('HLS error:', data)
          if (data.fatal) {
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                setError('Network error loading stream')
                hls.startLoad()
                break
              case Hls.ErrorTypes.MEDIA_ERROR:
                setError('Media error - trying to recover')
                hls.recoverMediaError()
                break
              default:
                setError('Fatal error occurred')
                hls.destroy()
                break
            }
          }
        })
      } else if (audio.canPlayType('application/vnd.apple.mpegurl')) {
        // Fallback for Safari which has native HLS support
        audio.src = streamUrl
        audio.play().catch(err => {
          console.error('Auto-play failed:', err)
          setError('Click play to start audio (browser blocked auto-play)')
        })
      } else {
        setError('HLS not supported in this browser')
      }
    } else {
      // Clean up when stream is inactive
      if (hlsRef.current) {
        hlsRef.current.destroy()
        hlsRef.current = null
      }
      audio.pause()
      audio.src = ''
    }

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy()
        hlsRef.current = null
      }
    }
  }, [isActive, streamUrl])

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume
    }
  }, [volume, isMuted])

  const toggleMute = () => {
    setIsMuted(!isMuted)
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value)
    setVolume(newVolume)
    if (newVolume > 0 && isMuted) {
      setIsMuted(false)
    }
  }

  const playPause = () => {
    if (!audioRef.current) return

    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play().catch(err => {
        console.error('Play failed:', err)
        setError('Failed to play audio stream')
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Audio Element */}
      <audio
        ref={audioRef}
        preload="none"
        className="hidden"
      />

      {/* Player Interface */}
      <div className="bg-slate-50 rounded-xl p-6 border border-slate-200/50">
        {/* Status Display */}
        <div className="text-center mb-6">
          {isLoading && (
            <div className="flex items-center justify-center space-x-2 text-slate-600">
              <div className="w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
              <span className="text-sm">Loading stream...</span>
            </div>
          )}

          {!isActive && !isLoading && (
            <div className="text-slate-500 text-sm">
              Stream not active. Start the translation to begin audio playback.
            </div>
          )}

          {isActive && !isLoading && !error && (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-slate-700">Live Stream Active</span>
            </div>
          )}

          {error && (
            <div className="text-red-600 text-sm flex items-center justify-center space-x-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Play/Pause Button */}
        <div className="flex justify-center mb-6">
          <button
            onClick={playPause}
            disabled={!isActive || isLoading}
            className={`
              w-16 h-16 rounded-full flex items-center justify-center
              transition-all duration-200 hover:scale-105 focus:outline-none
              focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:hover:scale-100
              ${isPlaying
                ? 'bg-primary-600 text-white shadow-lg shadow-primary-500/25'
                : 'bg-white border-2 border-primary-600 text-primary-600 hover:bg-primary-50'
              }
            `}
          >
            {isPlaying ? (
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>
        </div>

        {/* Volume Controls */}
        <div className="flex items-center space-x-4 max-w-xs mx-auto">
          <button
            onClick={toggleMute}
            className="p-2 text-slate-600 hover:text-slate-800 transition-colors"
          >
            {isMuted ? (
              <SpeakerXMarkIcon className="w-5 h-5" />
            ) : (
              <SpeakerWaveIcon className="w-5 h-5" />
            )}
          </button>

          <div className="flex-1">
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>

          <div className="text-sm text-slate-600 w-10 text-right">
            {Math.round((isMuted ? 0 : volume) * 100)}%
          </div>
        </div>
      </div>

      {/* Stream Info */}
      <div className="text-center text-xs text-slate-500">
        {isActive && (
          <>
            Stream URL: <code className="bg-slate-100 px-2 py-1 rounded">{streamUrl}</code>
            <br />
            <span className="text-slate-400">
              Using {Hls.isSupported() ? 'HLS.js' : 'Native HLS'} for playback
            </span>
          </>
        )}
      </div>
    </div>
  )
}