# 🤖 Smart Summarizer

![Smart Summarizer](https://github.com/joblas/flask_summarizer/blob/main/Screenshot%20Smart%20Summarizer.png)

Smart Summarizer is a Flask-based web application that provides concise summaries of web pages and YouTube videos. It uses advanced natural language processing techniques to generate accurate and relevant summaries. 📚✨

## ✨ Features

- 🌐 Summarize content from any web page URL
- 🎥 Summarize YouTube videos using transcript data
- 📏 Adjustable summary length (min and max characters)
- 🖥️ User-friendly web interface
- 📱 Responsive design with gradient background

## 🚀 Installation

1. Clone the repository:

git clone https://github.com/joblas/flask_summarizer.git

cd smart-summarizer


2. Create and activate a virtual environment:

python -m venv venv

source venv/bin/activate 

# On Windows use venv\Scripts\activate


3. Install the required packages:

pip install flask transformers torch flask_sqlalchemy youtube_transcript_api beautifulsoup4 flask_cors bert-extractive-summarizer sentencepiece

pip install -r requirements.txt


## 🎯 Usage

1. Start the Flask application:
flask run

2. 🌐 Open a web browser and navigate to `http://127.0.0.1:5000/`

3. 📝 Enter a URL in the input field (web page or YouTube video)

4. ⚙️ Adjust the min and max summary length if desired

5. 🖱️ Click the "Summarize" button to generate a summary

## 🛠️ Technologies Used

- 🌶️ Flask: Web framework
- 🤗 Transformers: For text summarization
- 🎥 YouTube Transcript API: For fetching YouTube video transcripts
- 🍲 BeautifulSoup: For web scraping
- 💻 HTML/CSS/JavaScript: For the frontend

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 👨‍💻👩‍💻

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- 🤗 [Hugging Face Transformers](https://github.com/huggingface/transformers) for the summarization model
- 🎥 [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for YouTube transcript fetching
