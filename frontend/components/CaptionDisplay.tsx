import { useEffect, useRef } from 'react'
import { ChatBubbleLeftIcon } from '@heroicons/react/24/outline'

interface Caption {
  timestamp: number
  text: string
  language: string
}

interface CaptionDisplayProps {
  captions: Caption[]
  isActive: boolean
}

export default function CaptionDisplay({ captions, isActive }: CaptionDisplayProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new captions arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [captions])

  const formatTimestamp = (timestamp: number) => {
    const minutes = Math.floor(timestamp / 60)
    const seconds = Math.floor(timestamp % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <div className="h-96 flex flex-col">
      {/* Header */}
      <div className="flex items-center space-x-2 mb-4">
        <ChatBubbleLeftIcon className="w-5 h-5 text-slate-600" />
        <span className="text-sm font-medium text-slate-700">Spanish Captions</span>
        {isActive && (
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        )}
      </div>

      {/* Captions Container */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-3 pr-2"
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: '#cbd5e1 #f1f5f9'
        }}
      >
        <style jsx>{`
          div::-webkit-scrollbar {
            width: 6px;
          }
          div::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 3px;
          }
          div::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
          }
          div::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
          }
        `}</style>

        {captions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400">
            <ChatBubbleLeftIcon className="w-12 h-12 mb-3 opacity-50" />
            <p className="text-sm text-center px-4">
              {isActive
                ? "Waiting for captions..."
                : "Start the stream to see live captions"
              }
            </p>
          </div>
        ) : (
          captions.map((caption, index) => (
            <div
              key={index}
              className="animate-slide-up"
            >
              <div className="bg-slate-50 rounded-lg p-3 border border-slate-200/50 hover:bg-slate-100 transition-colors">
                <div className="text-xs text-slate-500 mb-1 font-mono">
                  {formatTimestamp(caption.timestamp)}
                </div>
                <div className="text-sm text-slate-800 leading-relaxed">
                  {caption.text}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-slate-200">
        <div className="text-xs text-slate-500 text-center">
          {captions.length > 0 && (
            <>
              {captions.length} caption{captions.length !== 1 ? 's' : ''} received
            </>
          )}
        </div>
      </div>
    </div>
  )
}