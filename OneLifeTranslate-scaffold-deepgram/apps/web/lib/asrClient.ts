export type AsrEvent = { isFinal: boolean; text: string }

export class AsrClient {
  constructor(private apiKey: string) {}
  start(_stream: MediaStream, _onEvent: (e: AsrEvent) => void) {
    // TODO: Implement Deepgram WebSocket streaming
  }
  stop() {
    // TODO: Stop stream
  }
}