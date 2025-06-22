import { CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/solid'

interface StreamStatus {
  status: 'not_initialized' | 'stopped' | 'running'
  captions_count: number
  connected_clients: number
  stream_start_time?: number
}

interface StatusIndicatorProps {
  status: StreamStatus | null
}

export default function StatusIndicator({ status }: StatusIndicatorProps) {
  if (!status) {
    return (
      <div className="flex items-center space-x-2">
        <div className="w-3 h-3 bg-gray-400 rounded-full" />
        <span className="text-sm text-gray-500">Loading...</span>
      </div>
    )
  }

  const getStatusInfo = () => {
    switch (status.status) {
      case 'running':
        return {
          icon: <CheckCircleIcon className="w-5 h-5 text-green-500" />,
          text: 'Stream Active',
          color: 'text-green-700',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200'
        }
      case 'stopped':
        return {
          icon: <XCircleIcon className="w-5 h-5 text-red-500" />,
          text: 'Stream Stopped',
          color: 'text-red-700',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200'
        }
      case 'not_initialized':
        return {
          icon: <ClockIcon className="w-5 h-5 text-yellow-500" />,
          text: 'Initializing',
          color: 'text-yellow-700',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200'
        }
      default:
        return {
          icon: <ClockIcon className="w-5 h-5 text-gray-500" />,
          text: 'Unknown',
          color: 'text-gray-700',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200'
        }
    }
  }

  const statusInfo = getStatusInfo()

  return (
    <div className={`
      flex items-center space-x-3 px-4 py-2 rounded-lg border
      ${statusInfo.bgColor} ${statusInfo.borderColor}
    `}>
      <div className="flex items-center space-x-2">
        {statusInfo.icon}
        <span className={`text-sm font-medium ${statusInfo.color}`}>
          {statusInfo.text}
        </span>
      </div>
      
      {status.status === 'running' && (
        <div className="flex items-center space-x-4 text-xs text-slate-600">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-primary-500 rounded-full" />
            <span>{status.connected_clients} clients</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full" />
            <span>{status.captions_count} captions</span>
          </div>
        </div>
      )}
    </div>
  )
}