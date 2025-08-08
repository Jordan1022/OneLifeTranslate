"use client"
import { useRef } from 'react'
import { AudioQueue } from '@/components/AudioQueue'

export function useAudioQueue() {
  const ref = useRef<AudioQueue>()
  if (!ref.current) ref.current = new AudioQueue()
  return ref.current
}