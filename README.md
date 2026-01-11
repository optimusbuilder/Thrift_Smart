# ThriftSmart AI - Your AI Shopping Copilot

> **Stop overpaying for thrift finds.** Upload a video, get instant price analysis powered by AI.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 The Problem

When thrifting or shopping secondhand, it's hard to know if you're getting a good deal. Is that laptop worth $250? What about that vintage jacket? **Most people overpay because they don't know the market value.**

## 💡 The Solution

**ThriftSmart AI** analyzes product videos in real-time, searches live marketplace data, and tells you if it's a **COP** (good deal) or **DROP** (overpriced) — complete with AI-powered voice analysis.

### ✨ Key Features

- 📹 **Video Product Recognition** - Upload any product video
- 🔍 **Live Market Research** - Scrapes eBay for real-time comparable prices  
- 🧠 **AI-Powered Analysis** - Uses Google Gemini to identify products and analyze deals
- 🎙️ **Voice Response** - Get spoken recommendations via ElevenLabs TTS
- ⚡ **Instant Verdict** - Clear COP/DROP decision with detailed reasoning
- 🎨 **Modern UI** - Beautiful glassmorphism design with smooth animations

## 🚀 Demo

https://github.com/user-attachments/assets/your-demo-video.mp4

*(Add a demo video or GIF here)*

### Example Analysis

**Input:** Video of HP EliteBook 840 G5 laptop, listed at $250

**Output:**
```
🔴 VERDICT: DROP

"That is an HP EliteBook 840 G5, equipped with an 8th Gen Intel Core i5 processor.

Market Value: Comparable units are selling right now for $120 to $170.

Your Price: $250

The Verdict: You would be significantly overpaying. For $250, you could easily 
find a much newer G7 or G8 model with significantly better performance. 

My Advice: Walk away from this one."
```

## 🛠️ Tech Stack

### Backend
- **Flask** - Web framework
- **Google Gemini 3.0 Pro** - Multimodal AI for video analysis
- **LangChain** - Agent orchestration
- **Selenium** - Web scraping (eBay price data)
- **ElevenLabs** - Text-to-speech for voice responses
- **Beautiful Soup** - HTML parsing

### Frontend
- **Vanilla JavaScript** - No framework overhead
- **Modern CSS** - Glassmorphism design
- **Font Awesome** - Icons
- **Custom Fonts** - Clash Display & General Sans

### AI Agent Tools
- Custom eBay product search tool
- Real-time price comparison engine
- Verdict decision algorithm

## 📦 Installation

### Prerequisites

- Python 3.9+
- Chrome/Chromium browser
- API Keys for:
  - Google AI (Gemini)
  - ElevenLabs

### Step 1: Clone the Repository

```bash
git clone https://github.com/optimusbuilder/thriftsmart-ai.git
cd thriftsmart-ai
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### Step 5: Install ChromeDriver

**macOS:**
```bash
brew install chromedriver
```

**Linux:**
```bash
sudo apt-get install chromium-chromedriver
```

**Windows:**
Download from [ChromeDriver](https://chromedriver.chromium.org/) and add to PATH.

### Step 6: Run the Application

```bash
python app.py
```

Open your browser to: `http://localhost:5001`

## 📁 Project Structure

```
thriftsmart-ai/
├── app.py                 # Flask backend & AI agent
├── system_prompt.py       # AI system instructions
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── static/
│   └── index.html        # Frontend interface
├── uploads/              # Temporary video storage (auto-created)
└── README.md             # You are here!
```

## 🎮 Usage

1. **Upload a Video** - Record or select a product video (MP4 format supported)
2. **Enter Store Price** - Type in the asking price
3. **Click "Check Value"** - Wait 30-60 seconds for analysis
4. **Get Your Verdict** - See if it's a COP or DROP + hear AI explanation

## 🧪 How It Works

### Architecture Flow

```
1. User uploads video + price
         ↓
2. Flask receives and saves video
         ↓
3. Video encoded to base64
         ↓
4. Gemini AI analyzes video content
         ↓
5. AI agent identifies product
         ↓
6. Selenium scrapes eBay (headless)
         ↓
7. AI compares prices & makes verdict
         ↓
8. ElevenLabs generates voice response
         ↓
9. Response sent to frontend
         ↓
10. User sees verdict + hears analysis
```

### AI Agent Decision Process

```python
1. Product Identification (Gemini Vision)
   └─> Extract: Brand, Model, Specs
   
2. Market Research (eBay Scraping)
   └─> Find: Comparable listings, Price range
   
3. Price Analysis (LangChain Agent)
   └─> Compare: User price vs Market price
   
4. Verdict Generation
   └─> If savings > 30%: COP ✅
   └─> If savings < 10%: DROP ❌
   
5. Voice Synthesis (ElevenLabs)
   └─> Convert text response to speech
```

## 🎨 Features Breakdown

### 1. Video Analysis
- Supports MP4
- Max file size: 500MB
- Uses Google Gemini's multimodal capabilities
- Identifies products from visual cues

### 2. Real-Time Price Scraping
- Headless Chrome browser (invisible)
- Searches eBay for comparable items
- Extracts product names and prices
- Returns top 10 most relevant results

### 3. AI Decision Making
- Analyzes market data vs asking price
- Considers product condition and age
- Provides detailed reasoning
- Clear COP/DROP recommendation

### 4. Voice Response
- Natural-sounding AI voice (ElevenLabs)
- Auto-plays analysis results
- Manual playback controls
- Visual waveform animation

### 5. Modern UI/UX
- Glassmorphism design
- Smooth animations
- Drag & drop file upload
- Loading states with spinner
- Responsive layout
- Proper error handling

## 🔧 Configuration

### Change Voice (ElevenLabs)

In `app.py`, modify:
```python
audio = elevenlabs.text_to_speech.convert(
    text=message_content,
    voice_id="EiNlNiXeDU1pqqOPrYMO",  # Change this
    model_id="eleven_multilingual_v2",
)
```

Available voices: [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)

### Adjust Verdict Threshold

In `app.py`, modify the `determine_verdict()` function:
```python
cop_keywords = ['good buy', 'good deal', 'cop', ...]
drop_keywords = ['drop', 'pass', 'overpriced', ...]
```

### Customize AI Behavior

Edit `system_prompt.py` to change how the AI analyzes products.

## 🐛 Troubleshooting

### ChromeDriver Issues
```bash
# Update Chrome
brew upgrade --cask google-chrome

# Reinstall ChromeDriver
brew reinstall chromedriver
```

### CORS Errors
Make sure you're accessing via `http://localhost:5001` (not `127.0.0.1`)

### Audio Not Playing
- Check browser console for errors
- Verify ElevenLabs API key is valid
- Click play button if auto-play is blocked
- Check system volume

### Video Upload Fails
- Ensure file size < 500MB
- Use supported formats only
- Check `uploads/` folder permissions

## 📊 Performance

- **Video Analysis**: ~10-15 seconds
- **eBay Scraping**: ~5-10 seconds
- **Voice Generation**: ~3-5 seconds
- **Total Processing**: ~30-60 seconds

*Processing time depends on video size, internet speed, and API response times.*

## 🚀 Future Enhancements

- [ ] Support for multiple marketplaces (Facebook Marketplace, Craigslist, etc.)
- [ ] Historical price tracking
- [ ] Product condition assessment
- [ ] Comparison with new product prices
- [ ] Save analysis history
- [ ] Mobile app version
- [ ] Chrome extension
- [ ] Batch analysis for multiple items
- [ ] Community price database
- [ ] AR product scanning

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@optimusbuilder](https://github.com/optimusbuilder)
- Email: oyeludeferanmi@gmail.com

## 🙏 Acknowledgments

- Google AI for Gemini API
- ElevenLabs for voice synthesis
- Anthropic Claude for development assistance
- The open-source community

## 📸 Screenshots

### Home Screen
![Home Screen](/Users/oluwaferanmioyelude/Documents/screenshot.png)


### Analysis Result
![Result](/Users/oluwaferanmioyelude/Documents/screenshot1)

---

**Built with ❤️**

⭐ Star this repo if you find it useful!


<p align="center">Made with 🔥 by [Your Name] | © 2026</p>