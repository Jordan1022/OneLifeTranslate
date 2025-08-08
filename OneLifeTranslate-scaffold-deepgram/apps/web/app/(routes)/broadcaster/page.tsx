"use client"
import { useEffect, useMemo, useRef, useState } from 'react'

export default function BroadcasterPage() {
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([])
  const [deviceId, setDeviceId] = useState<string>('')
  const [isLive, setIsLive] = useState(false)
  const mediaStreamRef = useRef<MediaStream | null>(null)

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then(list => {
      setDevices(list.filter(d => d.kind === 'audioinput'))
    }).catch(() => {})
  }, [])

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: deviceId ? { deviceId: { exact: deviceId } } : true })
    mediaStreamRef.current = stream
    setIsLive(true)
    // TODO: wire to ASR streaming client
  }
  function stop() {
    mediaStreamRef.current?.getTracks().forEach(t => t.stop())
    mediaStreamRef.current = null
    setIsLive(false)
  }

  return (
    <main className="p-4 space-y-4">
      <h1 className="text-xl font-semibold">Broadcaster</h1>
      <div className="flex items-center gap-2">
        <select className="px-3 py-2 rounded bg-neutral-800 border border-neutral-700" value={deviceId} onChange={e => setDeviceId(e.target.value)}>
          <option value="">Default input</option>
          {devices.map(d => <option key={d.deviceId} value={d.deviceId}>{d.label || d.deviceId}</option>)}
        </select>
        {isLive ? (
          <button className="px-3 py-2 rounded bg-rose-600" onClick={stop}>Stop</button>
        ) : (
          <button className="px-3 py-2 rounded bg-emerald-600" onClick={start}>Go live</button>
        )}
      </div>
      <p className="text-neutral-400 text-sm">Grant microphone permissions to enumerate devices.</p>
    </main>
  )
}