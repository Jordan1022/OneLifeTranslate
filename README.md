# OneLife Translation Stream

Real-time English→Spanish translation system for church services with modern, minimalist web interface.

![OneLife Translation](https://img.shields.io/badge/Status-Ready-green)
![Version](https://img.shields.io/badge/Version-0.3.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Overview

This system provides real-time translation from English to Spanish for church services, featuring:

- **Audio Capture**: Dante Virtual Soundcard integration
- **Speech-to-Text**: OpenAI Whisper API
- **Translation**: GPT-4o Mini with custom church glossary
- **Text-to-Speech**: ElevenLabs with Latin American Spanish voice
- **Streaming**: HLS with synchronized live captions
- **Modern UI**: Minimalist web interface built with Next.js and Tailwind CSS

## 🏗️ Architecture

```
Mixer Dante BUS → Translation PC → Whisper API → GPT-4o Mini → ElevenLabs TTS → HLS Stream → Web Client
                                  ↓
                              Glossary Filter
                                  ↓
                            Live Captions (SSE)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg
- Dante Virtual Soundcard (for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd onelife-translate
   ```

2. **Setup Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Open the web interface**
   - Navigate to `http://localhost:8000`
   - Click "Start Stream" to begin translation

## ⚙️ Configuration

### Environment Variables

```bash
# Required for production
OPENAI_API_KEY=sk-your-openai-api-key-here
ELEVEN_API_KEY=your-elevenlabs-api-key-here

# Optional settings
USE_MOCK=true              # Use mock services for testing
HOST=0.0.0.0              # Server host
PORT=8000                 # Server port
LOG_LEVEL=INFO            # Logging level
```

### Glossary

Edit `glossary.csv` to customize translations for church-specific terms:

```csv
en,es
Holy Spirit,Espíritu Santo
Lord's Supper,Cena del Señor
tithes and offerings,diezmos y ofrendas
```

## 🎛️ Dante Setup

### Audio Routing

1. **Install Dante Virtual Soundcard** on translation PC
2. **Configure mixer** to send AUX/Matrix output to Dante network
3. **Route audio** in Dante Controller:
   - Source: Mixer AUX output
   - Destination: DVS Input 1-2
4. **Verify audio** is reaching the translation PC

### Network Configuration

- Use dedicated Dante network switch
- Set static IP addresses for stable connections
- Enable PTP (Precision Time Protocol) for synchronization

## 🖥️ Web Interface

### Features

- **Modern Design**: Clean, minimalist interface
- **Real-time Status**: Live indicators for system health
- **Audio Controls**: Volume, play/pause, stream management
- **Live Captions**: Synchronized Spanish text display
- **Responsive**: Works on desktop, tablet, and mobile devices

### Usage

1. **Start Stream**: Click the play button to begin translation
2. **Monitor Status**: Check connection and processing indicators
3. **Adjust Volume**: Use the volume slider for audio output
4. **View Captions**: Read synchronized Spanish translations
5. **Stop Stream**: Click stop when service ends

## 🔧 Development

### Running in Development Mode

```bash
# Backend (with hot reload)
cd streamer
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Frontend (in separate terminal)
cd frontend
npm run dev
```

### Mock Mode

For development without API keys:

```bash
export USE_MOCK=true
python main.py
```

Mock services simulate:
- Audio capture with silent audio
- Speech recognition with test phrases
- Translation with sample Spanish text
- TTS with silent audio output

## 📊 Performance

### Latency Targets

| Component | Target | Typical |
|-----------|---------|---------|
| Audio capture | 1ms | 1ms |
| Whisper API | 300ms | 250ms |
| Translation | 150ms | 120ms |
| TTS first byte | 200ms | 180ms |
| HLS buffering | 400ms | 300ms |
| **Total glass-to-glass** | **~1.1s** | **~0.9s** |

### Scaling

- **Single service**: 50-100 concurrent clients
- **Load balancing**: Multiple translation PCs
- **CDN**: Cloudflare for global distribution

## 🛠️ Troubleshooting

### Common Issues

**Audio not capturing:**
- Check Dante Virtual Soundcard installation
- Verify audio routing in Dante Controller
- Ensure DVS appears in system audio devices

**API errors:**
- Validate API keys in `.env` file
- Check internet connectivity
- Monitor API usage limits

**Stream not playing:**
- Verify FFmpeg installation
- Check HLS segment generation in `/stream` folder
- Test with direct audio element

**Captions not updating:**
- Check WebSocket/SSE connections
- Verify backend processing logs
- Test with mock mode first

### Logs

Check logs for debugging:
- Application log: `translation_stream.log`
- Network requests in browser dev tools
- System audio devices in OS settings

## 📋 Production Checklist

- [ ] Dante Virtual Soundcard installed and configured
- [ ] API keys set in production environment
- [ ] FFmpeg installed and accessible
- [ ] Network configured for Dante audio
- [ ] Backup translation PC ready
- [ ] Test run before service
- [ ] Volume levels adjusted
- [ ] Client devices tested

## 🔐 Security

- API keys stored securely in environment variables
- HTTPS recommended for production deployment
- CORS configured for specific origins
- Rate limiting on API endpoints
- Input validation on all user data

## 📈 Monitoring

### Health Checks

- `/status` endpoint for system health
- Connection monitoring for Dante audio
- API response time tracking
- Client connection counts
- Stream quality metrics

### Metrics

- Translation accuracy (manual review)
- End-to-end latency measurements
- Client engagement analytics
- Error rates and recovery times

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🎯 Roadmap

- [ ] Moderator dashboard for corrections
- [ ] Auto-archive to bilingual subtitles
- [ ] Redundant Dante connections
- [ ] Multi-language support
- [ ] Advanced audio processing
- [ ] Analytics dashboard

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review application logs
- Test with mock mode
- Contact: Jordan @ Goodly Dev

---

**Built with ❤️ for OneLife Church**

*Connecting communities through real-time translation*