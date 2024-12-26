# Speech Concept Detector

A real-time speech recognition web application that detects and highlights specific concepts or keywords while providing their definitions using GPT-4.

## Features

- Real-time speech recognition and transcription
- Keyword highlighting
- Dynamic definition tooltips using GPT-4
- Interactive web interface using React
- Real-time statistics tracking

## Technologies Used

- Python/Flask for backend
- React for frontend
- OpenAI GPT-4 API for definitions
- Web Speech API for speech recognition
- TailwindCSS for styling

## Setup

1. Clone the repository:
```bash
git clone https://github.com/nikol12ro/speech-concept-detector.git
cd speech-concept-detector
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory and add:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python final_script.py
```

5. Open your browser and go to `http://localhost:5000`

## Usage

1. Enter keywords or concepts in the context area
2. Click "Load Context" to initialize
3. Click "Record" to start speech recognition
4. Speak into your microphone
5. Hover over highlighted words to see their definitions

## Note
- Speech recognition requires Chrome browser
- An active internet connection is required for GPT-4 definitions