from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import re
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paragraphs = soup.find_all("p")
    text = " ".join([p.get_text() for p in paragraphs])
    return text

def get_youtube_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = " ".join([entry['text'] for entry in transcript])
    return transcript_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        print("Received data:", request.get_json())
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        url = data.get('url')
        max_length = data.get('max_length', 300)  # Default to 300 if not provided
        min_length = data.get('min_length', 100)  # Default to 100 if not provided
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        if "youtube.com" in url or "youtu.be" in url:
            video_id = extract_video_id(url)
            if not video_id:
                return jsonify({"error": "Invalid YouTube URL"}), 400
            text = get_youtube_transcript(video_id)
        else:
            text = get_text_from_url(url)
        
        if not text:
            return jsonify({"error": "Could not extract text from the URL"}), 400
        
        # Increase the maximum input length to 4096
        if len(text) > 4096:
            text = text[:4096]
        
        summary = summarizer(text, max_length=int(max_length), min_length=int(min_length), do_sample=False)
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_video_id(url):
    regex = (
        r"(https?://)?(www\.)?"
        "(youtube|youtu|youtube-nocookie)\.(com|be)/"
        "(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})")
    match = re.match(regex, url)
    if match:
        return match.group(6)
    return None

if __name__ == '__main__':
    app.run(debug=True)
