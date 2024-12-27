# Speech Concept Detector

A speech-to-text application that transforms your spoken words into interactive transcripts. As you speak, the application transcribes your speech in real-time, automatically highlighting user-defined keywords and providing instant GPT-4-powered definitions through tooltips. Perfect for learning, presentations, or tracking specific terms in conversations.

## Key Features

- Live Speech Transcription
  - Real-time conversion of speech to text
  - Support for continuous speech recognition
  - Clear, readable transcript display

- Smart Keyword Detection
  - Customizable keyword list
  - Automatic highlighting of matched terms
  - Real-time match statistics

- Interactive Learning
  - Hover-activated definition tooltips
  - GPT-4 powered explanations

- User-Friendly Interface
  - Clean, modern React design
  - Real-time statistics tracking
  - Easy transcript management

## Technologies

- Backend: Python/Flask
- Frontend: React 
- AI Integration: OpenAI GPT-4 API
- Speech Recognition: Web Speech API
- Styling: TailwindCSS

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/nikol12ro/speech_concept_detector.git
cd speech_concept_detector
```

2. Set up Python environment (recommended):
```bash
conda create -n speech_detector python=3.10
conda activate speech_detector
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure OpenAI API:
Create a `.env` file in the root directory and add:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
python final_script.py
```

6. Access the app:
Open your browser and navigate to `http://127.0.0.1:5000`

## How to Use

1. Start Up
   - Enter keywords you want to track in the context area
   - Click "Load Context" to initialize the detection system

2. Recording
   - Click the "Record" button to start speech recognition
   - Speak naturally into your microphone
   - Watch as your speech is transcribed in real-time

3. Interaction
   - Spoken words matching your keywords will be highlighted
   - Hover over highlighted words to see their definitions
   - Track matches and word count in real-time

4. Management
   - Use the clear button to reset the transcript
   - Stop and start recording as needed
   - Update keywords anytime by loading new context

## Requirements

- Browser: Google Chrome (required for speech recognition)
- Internet Connection: Required for GPT-4 definitions
- OpenAI API Key: Required for definition generation
