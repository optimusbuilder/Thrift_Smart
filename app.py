from dotenv import load_dotenv
load_dotenv()
from system_prompt import system_instruction
import os
import time
import base64
import traceback

# Load environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
PARSE_API_KEY = os.getenv("PARSE_API_KEY")
os.environ["PARSE_API_KEY"] = PARSE_API_KEY
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
os.environ["ELEVENLABS_API_KEY"] = ELEVENLABS_API_KEY
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# Import AI/ML libraries
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from tavily import TavilyClient
from elevenlabs.client import ElevenLabs
from langchain_google_genai import ChatGoogleGenerativeAI

# Import Selenium for web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Import Flask
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Initialize clients
client = TavilyClient()
elevenlabs = ElevenLabs()

# Initialize Gemini model
model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    temperature=1.0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# TOOLS


@tool
def get_product_data(search_query: str) -> dict:
    """
    Opens eBay, searches for the specific `search_query`, 
    and returns a dictionary of {Product Name: Price}.
    """
    try:
        # Setup Chrome options for headless mode
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.ebay.com/")
        time.sleep(3)
        
        search_box = driver.find_element(By.XPATH, '//*[@id="gh-ac"]')
        search_box.send_keys(search_query)
        
        search_button = driver.find_element(By.XPATH, '//*[@id="gh-search-btn"]')
        search_button.click()
        time.sleep(2)
        
        page_source = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(page_source, 'html.parser')
        prices = soup.find_all("span", class_="su-styled-text primary bold large-1 s-card__price")
        names = soup.find_all("span", class_="su-styled-text primary default")
        
        price_dict = {}
        for price, name in zip(prices, names):
            price_dict[name.get_text()] = price.get_text()
        
        return price_dict
    except Exception as e:
        print(f"Error in get_product_data: {e}")
        return {"error": str(e)}

# CREATE AGENT

agent = create_agent(
    model=model, 
    system_prompt=system_instruction,
    tools=[get_product_data],
    checkpointer=InMemorySaver()
)


# FLASK SETUP

app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HELPER FUNCTIONS

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_message_for_display(text):
    """
    Format the AI message to be more readable in HTML.
    Converts markdown-style formatting to HTML.
    """
    import re
    
    # Replace **text** with <strong>text</strong>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Replace *text* with <em>text</em>
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    
    # Split into paragraphs (double newline or bullet points)
    paragraphs = []
    current_para = []
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            if current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
        elif line.startswith('*') or line.startswith('-'):
            # Bullet point
            if current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
            paragraphs.append(f"• {line.lstrip('*-').strip()}")
        else:
            current_para.append(line)
    
    if current_para:
        paragraphs.append(' '.join(current_para))
    
    # Join with line breaks
    return '<br><br>'.join(paragraphs)

def extract_text_from_content(content):
    """
    Extract plain text from various content formats returned by the agent.
    Handles: strings, dicts, lists of dicts
    """
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # List of content blocks
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                return item.get('text', '')
        # If no text block found, try first item
        if content and isinstance(content[0], dict):
            return content[0].get('text', str(content[0]))
        return str(content)
    elif isinstance(content, dict):
        return content.get('text', str(content))
    return str(content)

def determine_verdict(text):
    """
    Determine if the product is a good buy (COP) or not (DROP)
    based on keywords in the agent's response.
    """
    text_lower = text.lower()
    
    # Positive indicators
    cop_keywords = [
        'good buy', 'good deal', 'cop', 'great price', 'worth it',
        'solid pickup', 'steal', 'underpriced', 'great find',
        'definitely buy', 'good value', 'fair price'
    ]
    
    # Negative indicators
    drop_keywords = [
        'drop', 'pass', 'skip', 'overpriced', 'not worth',
        'too expensive', 'bad deal', 'overpaying', 'walk away',
        'hard pass', 'avoid', 'stay away'
    ]
    
    # Check for DROP keywords
    for keyword in drop_keywords:
        if keyword in text_lower:
            return 'DROP'
    
    # Then check for COP keywords
    for keyword in cop_keywords:
        if keyword in text_lower:
            return 'COP'
    
    # Default to neutral if unclear
    return 'REVIEW'

# ROUTES


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """Main endpoint for analyzing product videos"""
    
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        print("\n" + "=" * 60)
        print("NEW ANALYSIS REQUEST")
        print("=" * 60)
        print(f"Files received: {list(request.files.keys())}")
        print(f"Form data: {dict(request.form)}")
        
        # Validate video file
        if 'video' not in request.files:
            return jsonify({'error': 'No video file uploaded'}), 400
        
        video = request.files['video']
        if video.filename == '':
            return jsonify({'error': 'No video selected'}), 400
        
        if not allowed_file(video.filename):
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Validate price
        price = request.form.get('price')
        if not price:
            return jsonify({'error': 'Price is required'}), 400
        
        try:
            price_float = float(price)
            if price_float <= 0:
                return jsonify({'error': 'Price must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid price format'}), 400
        
        # Save video file
        filename = secure_filename(video.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(video_path)
        print(f"✓ Video saved: {video_path}")
        print(f"✓ Price: ${price}")
        
        # Read and encode video
        print("→ Encoding video...")
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        video_base64 = base64.b64encode(video_bytes).decode("utf-8")
        mime_type = "video/mp4"
        
        # Create message for agent
        message = HumanMessage(content=[
            {
                "type": "text", 
                "text": f"I saw this item for ${price}. Is it a good buy? Please analyze the video and search eBay for comparable prices."
            },
            {
                "type": "video",
                "base64": video_base64,
                "mime_type": mime_type,
            },
        ])
        
        # Invoke agent
        print("→ Invoking AI agent (this may take 30-60 seconds)...")
        config = {"configurable": {"thread_id": "1"}}
        agent_response = agent.invoke({"messages": [message]}, config)
        
        # Extract text content
        raw_content = agent_response['messages'][-1].content
        message_content = extract_text_from_content(raw_content)
        
        print(f"✓ Agent response received ({len(message_content)} chars)")
        print(f"Preview: {message_content[:150]}...")
        
        # Format message for better display
        formatted_message = format_message_for_display(message_content)
        
        # Determine verdict
        verdict = determine_verdict(message_content)
        print(f"✓ Verdict: {verdict}")
        
        # Generate audio
        print("→ Generating audio with ElevenLabs...")
        try:
            audio = elevenlabs.text_to_speech.convert(
                text=message_content,
                voice_id="8JVbfL6oEdmuxKn5DK2C",
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            
            # Convert audio iterator to bytes
            audio_bytes = b""
            for chunk in audio:
                audio_bytes += chunk
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            print(f"✓ Audio generated ({len(audio_bytes)} bytes)")
            
        except Exception as audio_error:
            print(f"Audio generation failed: {audio_error}")
            print("Continuing without audio...")
            audio_base64 = None
        
        # Clean up video file
        try:
            os.remove(video_path)
            print(f"✓ Cleaned up: {video_path}")
        except Exception as cleanup_error:
            print(f"⚠ Cleanup failed: {cleanup_error}")
        
        # Prepare response
        response_data = {
            'verdict': verdict,
            'message': formatted_message,  # Use formatted version for display
            'audio': audio_base64
        }
        
        print("✓ Sending response to frontend")
        print("=" * 60 + "\n")
        return jsonify(response_data), 200
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR OCCURRED")
        print("=" * 60)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        print("=" * 60 + "\n")
        
        return jsonify({
            'error': f'{type(e).__name__}: {str(e)}',
            'message': 'An error occurred while analyzing the video. Please try again.'
        }), 500

# RUN SERVER


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("THRIFTSMART AI SERVER")
    print("=" * 60)
    print(f"→ Server running at: http://localhost:5001")
    print(f"→ Static files from: {os.path.abspath('static')}")
    print(f"→ Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print("→ Make sure 'static/index.html' exists")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')