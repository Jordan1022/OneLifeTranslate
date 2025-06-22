# OneLife Translation - Deployment Guide

## 🔐 Authentication System

Your app now includes token-based authentication to protect against unauthorized API usage. Users will access the translation service via QR codes or NFC tags with embedded authentication tokens.

## 🚀 Vercel Deployment

### 1. Prepare for Deployment

```bash
# Install dependencies
cd frontend
npm install

# Build the frontend
npm run build

# Go back to root
cd ..

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Up Vercel Project

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### 3. Configure Environment Variables

In your Vercel dashboard, add these environment variables:

**Required:**
- `AUTH_SECRET`: `your-super-secure-random-string-here`
- `OPENAI_API_KEY`: Your OpenAI API key
- `ELEVEN_API_KEY`: Your ElevenLabs API key

**Optional:**
- `USE_MOCK`: `false` (set to `true` for testing without real APIs)

### 4. Generate Access Tokens

Run the token generator to create QR code URLs:

```bash
python generate_tokens.py
```

This will output:
- Valid access tokens
- Sample URLs for QR codes
- Security recommendations

## 🔗 Creating QR Codes

### Example URLs:
```
https://your-app.vercel.app?token=onelife-spanish-access
https://your-app.vercel.app?token=church-translation-2024
https://your-app.vercel.app?token=week-47-2024
```

### QR Code Services:
- [QR Code Generator](https://www.qr-code-generator.com/)
- [QRCode Monkey](https://www.qrcode-monkey.com/)
- Google Charts API: `https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl=YOUR_URL`

## 📱 NFC Tag Setup

For NFC tags, program them with the URL including the token:
```
https://your-app.vercel.app?token=onelife-spanish-access
```

## 🔒 Security Features

### Built-in Protection:
1. **Token Validation**: All API endpoints require valid tokens
2. **Weekly Rotation**: Tokens automatically rotate weekly
3. **Multiple Token Support**: Main, alternative, and time-based tokens
4. **HMAC Security**: Tokens can be hashed for additional security
5. **Access Control**: Only authenticated users can start/stop streams

### Security Recommendations:
1. **Keep tokens private** - Only share with authorized church members
2. **Rotate regularly** - Update QR codes periodically
3. **Monitor usage** - Check Vercel analytics for unusual activity
4. **Remove debug endpoints** - Delete `/auth/tokens` endpoint in production
5. **Set CORS properly** - Update CORS origins for your domain

## 🛠 Production Checklist

### Before Go-Live:
- [ ] Set strong `AUTH_SECRET` environment variable
- [ ] Configure real API keys (OpenAI, ElevenLabs)
- [ ] Set `USE_MOCK=false`
- [ ] Update CORS origins in `streamer/api.py`
- [ ] Remove or protect `/auth/tokens` endpoint
- [ ] Test token validation
- [ ] Generate and test QR codes
- [ ] Set up monitoring/alerts

### Post-Deployment:
- [ ] Print QR codes for church distribution
- [ ] Program NFC tags if using
- [ ] Train church staff on usage
- [ ] Monitor API usage and costs
- [ ] Set up regular token rotation schedule

## 🔄 Token Management

### Current Tokens:
1. **Main**: `onelife-spanish-access`
2. **Alternative**: `church-translation-2024`
3. **Weekly**: `week-[number]-2024` (auto-rotates)

### To Add New Tokens:
Edit the `_generate_valid_tokens()` method in `streamer/api.py`:

```python
base_tokens = [
    'onelife-spanish-access',
    'church-translation-2024',
    'your-new-token-here',  # Add here
]
```

### To Rotate Tokens:
1. Add new tokens to the code
2. Deploy updated version
3. Generate new QR codes
4. Distribute new QR codes
5. Remove old tokens after transition period

## 📊 Monitoring

### Check API Usage:
- Vercel Dashboard: Function invocations
- OpenAI Dashboard: API usage and costs
- ElevenLabs Dashboard: Character usage

### Error Monitoring:
- Check Vercel function logs
- Monitor failed authentication attempts
- Set up alerts for high API usage

## 🆘 Troubleshooting

### Common Issues:

**"Invalid access token"**
- Check token spelling in QR code
- Verify token is in valid tokens list
- Ensure AUTH_SECRET matches between environments

**"Connection refused"**
- Check API URL in Next.js config
- Verify Vercel deployment status
- Check CORS configuration

**High API costs**
- Monitor token sharing
- Check for unauthorized usage
- Consider implementing rate limiting

**Audio streaming issues**
- Verify HLS stream generation
- Check browser compatibility
- Test network connectivity

## 📞 Support

For deployment issues:
1. Check Vercel deployment logs
2. Verify environment variables
3. Test locally first
4. Check this guide for common solutions

For authentication issues:
1. Regenerate tokens with `generate_tokens.py`
2. Verify token in QR code
3. Check API logs for authentication errors

---

**Next Steps:**
1. Deploy to Vercel
2. Set environment variables
3. Generate access tokens
4. Create QR codes for church members
5. Test with congregation
6. Monitor usage and costs 