from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import re
from flask_cors import CORS
from datetime import datetime, timezone
import os

app = Flask(__name__, static_folder='static')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///summaries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FAVICON'] = os.path.join(app.root_path, 'static', 'favicon')
db = SQLAlchemy(app)

models = {
    'bart': pipeline("summarization", model="facebook/bart-large-cnn"),
    't5': pipeline("summarization", model="t5-small"),
    'pegasus': pipeline("summarization", model="google/pegasus-xsum")
}

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Summary {self.url}>'

with app.app_context():
    db.create_all()

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
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        url = data.get('url')
        model_name = data.get('model', 'bart')
        
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
        
        if len(text) > 4096:
            text = text[:4096]
        
        summary = models[model_name](text, max_length=300, min_length=50, do_sample=False)
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summarize_file', methods=['POST'])
def summarize_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        text = file.read().decode('utf-8')
        model_name = request.form.get('model', 'bart')
        
        # Split the text into chunks if it's too long
        max_input_length = 1024  # This value might need to be adjusted based on the model
        chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length)]
        
        summaries = []
        for chunk in chunks:
            summary = models[model_name](chunk, max_length=300, min_length=50, do_sample=False)
            summaries.extend(summary)
        
        # Combine the summaries if there are multiple
        final_summary = " ".join([s['summary_text'] for s in summaries])
        
        # Truncate the final summary if it's too long
        if len(final_summary) > 300:
            final_summary = final_summary[:300]
        
        return jsonify([{"summary_text": final_summary}])

@app.route('/save_summary', methods=['POST'])
def save_summary():
    data = request.json
    new_summary = Summary(
        url=data['url'], 
        summary_text=data['summary'],
        created_at=datetime.now(timezone.utc)
    )
    db.session.add(new_summary)
    db.session.commit()
    return jsonify({"message": "Summary saved successfully"}), 200

@app.route('/history')
def get_history():
    summaries = Summary.query.order_by(Summary.created_at.desc()).limit(10).all()
    return jsonify([
        {
            "url": s.url, 
            "summary": s.summary_text, 
            "created_at": s.created_at.replace(tzinfo=timezone.utc).isoformat()
        }
        for s in summaries
    ])

def extract_video_id(url):
    regex = (
        r"(https?://)?(www\.)?"
        "(youtube|youtu|youtube-nocookie)\.(com|be)/"
        "(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})")
    match = re.match(regex, url)
    if match:
        return match.group(6)
    return None

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.config['FAVICON'], 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)