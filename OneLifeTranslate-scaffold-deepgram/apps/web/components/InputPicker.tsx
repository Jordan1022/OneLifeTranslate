"use client"
import { useEffect, useState } from 'react'

export function InputPicker({ value, onChange }: { value?: string, onChange: (id: string) => void }) {
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([])

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then(list => {
      setDevices(list.filter(d => d.kind === 'audioinput'))
    }).catch(() => {})
  }, [])

  return (
    <select className="px-3 py-2 rounded bg-neutral-800 border border-neutral-700" value={value} onChange={e => onChange(e.target.value)}>
      <option value="">Default input</option>
      {devices.map(d => (
        <option key={d.deviceId} value={d.deviceId}>{d.label || d.deviceId}</option>
      ))}
    </select>
  )
}