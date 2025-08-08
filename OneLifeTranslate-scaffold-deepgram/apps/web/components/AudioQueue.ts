export class AudioQueue {
  private queue: string[] = []
  private isPlaying = false

  enqueue(url: string) {
    this.queue.push(url)
    this.playNext()
  }

  private async playNext() {
    if (this.isPlaying || this.queue.length === 0) return
    this.isPlaying = true
    const url = this.queue.shift()!
    const audio = new Audio(url)
    await new Promise<void>((resolve) => {
      audio.onended = () => resolve()
      audio.onerror = () => resolve()
      audio.play().catch(() => resolve())
    })
    this.isPlaying = false
    this.playNext()
  }
}