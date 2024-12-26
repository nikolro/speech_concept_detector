from flask import Flask, request, jsonify
from markupsafe import Markup
from flask_cors import CORS
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def create_dictionary_with_gpt4(words_list):
    try:
        # Convert words_list to proper format if it's a string
        if isinstance(words_list, str):
            words_list = [word.strip() for word in words_list.split(',') if word.strip()]
        elif isinstance(words_list, (list, tuple, set)):
            words_list = [str(word).strip() for word in words_list if str(word).strip()]
        else:
            raise ValueError("words_list must be a string, list, tuple, or set")

        # Don't process if no valid words
        if not words_list:
            return {}

        # Create the system prompt
        system_prompt = f"""
        You are a dictionary expert. For each word in this list: {words_list},
        provide a clear, concise, and accurate definition.
        Rules:
        1. Focus on the most common meaning unless context suggests otherwise
        2. Keep definitions clear and understandable
        3. Format exactly as shown:
        DEFINITIONS:
        word1: definition1
        word2: definition2
        Only include words from the provided list. Do not add extra words.
        """
        # Make API call to GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ", ".join(words_list)}
            ],
            temperature=0.7  # Balanced between creativity and consistency
        )
        
        # Process the response
        content = response.choices[0].message.content
        
        # Parse the definitions into a dictionary
        definitions = {}
        if 'DEFINITIONS:' in content:
            lines = content.split('DEFINITIONS:')[1].strip().split('\n')
            for line in lines:
                if ':' in line:
                    word, definition = line.split(':', 1)
                    # Remove any part of speech indicators if they exist
                    cleaned_definition = definition.strip()
                    if cleaned_definition.startswith('('):
                        pos_end = cleaned_definition.find(')')
                        if pos_end != -1:
                            cleaned_definition = cleaned_definition[pos_end + 1:].strip()
                    definitions[word.strip()] = cleaned_definition

        return definitions

    except Exception as e:
        print(f"Error in create_dictionary_with_gpt4: {str(e)}")
        return None


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Enhanced Speech Concept Detector</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .tooltip {
            position: relative;
            display: inline-block;
        }
        .tooltip-content {
            position: fixed;
            z-index: 9999;
            background: black;
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 14px;
            pointer-events: none;
            white-space: normal;
            max-width: 300px;
        }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        function App() {
            const [context, setContext] = React.useState('');
            const [transcript, setTranscript] = React.useState('');
            const [isRecording, setIsRecording] = React.useState(false);
            const [keywords, setKeywords] = React.useState(new Set());
            const [status, setStatus] = React.useState('Ready');
            const [error, setError] = React.useState('');
            const [total, setTotal] = React.useState(0);
            const [matches, setMatches] = React.useState(0);
            const [tooltipContent, setTooltipContent] = React.useState(null);
            const [definitions, setDefinitions] = React.useState({});
            const [isLoadingDefinitions, setIsLoadingDefinitions] = React.useState(false);
            
            const recognitionRef = React.useRef(null);

            const checkBrowserSupport = () => {
                if (!('webkitSpeechRecognition' in window)) {
                    setError('Speech recognition is not supported in this browser. Please use Chrome.');
                    return false;
                }
                return true;
            };

    // Move useEffect to component level
    React.useEffect(() => {
    }, [definitions]);

    // Update getDefinitions function to handle loading state
    const getDefinitions = async (keywordsList) => {
        try {
            setIsLoadingDefinitions(true); // Start loading
            const response = await fetch('/get_definitions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    keywords: Array.from(keywordsList)
                }),
            });
            
            const data = await response.json();
            
            if (data.error) {
                console.error('Error getting definitions:', data.error);
                return;
            }
            
            setDefinitions(data.definitions);
        } catch (error) {
            console.error('Error fetching definitions:', error);
        } finally {
            setIsLoadingDefinitions(false); // End loading
        }
    };

        // Modify the loadContext function to call getDefinitions
        const loadContext = () => {
            if (!context.trim()) {
                setError('Please enter context text');
                return;
            }
            
            // Clean and process keywords
            const words = context
                .split(/[,\s]+/)
                .map(word => word.trim())
                .filter(word => word);
            
            // Create the keywords Set
            const newKeywords = new Set(
            words.map(w => w.toLowerCase())
            );
            
            setKeywords(newKeywords);
            
            // Get definitions for the keywords
            getDefinitions(newKeywords);
            
            setStatus('Context loaded');
            setError('');
            updateStats('');
        };

            const updateStats = (newText) => {
                const words = (transcript + newText).split(/\s+/).filter(w => w.trim());
                setTotal(words.length);
            };

            const startRecording = () => {
                if (!checkBrowserSupport()) return;
                if (!keywords.size) {
                    setError('Please load context first');
                    return;
                }

                try {
                    recognitionRef.current = new webkitSpeechRecognition();
                    const recognition = recognitionRef.current;
                    recognition.continuous = true;
                    recognition.interimResults = true;
                    recognition.lang = 'en-US';

                    recognition.onresult = async (event) => {
                        let newTranscript = '';
                        for (let i = event.resultIndex; i < event.results.length; i++) {
                            if (event.results[i].isFinal) {
                                const text = event.results[i][0].transcript;
                                newTranscript += text + ' ';
                            }
                        }

                        const processedText = highlightKeywords(newTranscript);
                        setTranscript(prev => prev + processedText);
                        updateStats(newTranscript);
                    };

                    recognition.onerror = (event) => {
                        setError(`Speech recognition error: ${event.error}`);
                        stopRecording();
                    };

                    recognition.onend = () => {
                        if (isRecording) {
                            recognition.start();
                        }
                    };

                    recognition.start();
                    setIsRecording(true);
                    setStatus('Recording...');
                    setError('');
                } catch (err) {
                    setError(`Failed to start recording: ${err.message}`);
                }
            };

            const stopRecording = () => {
                if (recognitionRef.current) {
                    recognitionRef.current.stop();
                }
                setIsRecording(false);
                setStatus('Stopped');
            };

        const highlightKeywords = (text) => {
            // Split text into words
            const words = text.split(/\s+/);

            let matchCount = 0; // Track matches

            const highlightedWords = words.map(word => {
                // Remove any punctuation and convert to lowercase
                const cleanWord = word.replace(/[.,!?]$/, '').toLowerCase();
                
                if (keywords.has(cleanWord)) {
                    matchCount++; // Increment matches when found
                    return `[highlight]${word}[/highlight]`;
                }
                return word;
            });

            setMatches(matchCount); // Update matches state
            return highlightedWords.join(' ');
        };

            const clearTranscript = () => {
                setTranscript('');
                setStatus('Transcript cleared');
                setStats({ total: 0, matches: 0 });
            };

            // Update handleMouseOver to show loading state
            const handleMouseOver = (event, word) => {
                const cleanWord = word.replace(/[.,!?]$/, '').toLowerCase();
                const rect = event.target.getBoundingClientRect();
                setTooltipContent({
                    text: isLoadingDefinitions 
                        ? "Loading definition..." 
                        : (definitions[cleanWord] || `Definition for: ${cleanWord}`),
                    x: rect.left + rect.width / 2,
                    y: rect.top - 10
                });
            };

            const handleMouseOut = () => {
                setTooltipContent(null);
            };

            return (
                <div className="container mx-auto px-4 py-8 max-w-4xl">
                    {error && (
                        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
                            <p>{error}</p>
                            <button 
                                onClick={() => setError('')}
                                className="float-right text-red-700 hover:text-red-900"
                            >
                                ×
                            </button>
                        </div>
                    )}

                    <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                        <div className="mb-4">
                            <div className="flex justify-between items-center mb-2">
                                <h2 className="text-xl font-bold">Context</h2>
                                <div className="flex items-center space-x-4">
                                </div>
                            </div>
                            <textarea
                                value={context}
                                onChange={(e) => setContext(e.target.value)}
                                placeholder="Enter keywords or phrases to detect..."
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                rows="3"
                            />
                            <button
                                onClick={loadContext}
                                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-2"
                            >
                                Load Context
                            </button>
                        </div>
                    </div>

                    <div className="bg-white shadow-md rounded px-8 pt-6 pb-8">
                        <div className="mb-4">
                            <div className="flex justify-between items-center mb-2">
                                <div className="flex items-center">
                                    <h2 className="text-xl font-bold mr-2">Transcript</h2>
                                    <span className="bg-gray-200 px-2 py-1 rounded text-sm">
                                        {matches}/{total} matches
                                    </span>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <span className={`px-2 py-1 rounded text-sm ${isRecording ? 'bg-red-200' : 'bg-gray-200'}`}>
                                        {status}
                                    </span>
                                    <button
                                        onClick={isRecording ? stopRecording : startRecording}
                                        className={`px-4 py-2 rounded ${isRecording ? 'bg-red-500 hover:bg-red-700' : 'bg-blue-500 hover:bg-blue-700'} text-white`}
                                    >
                                        {isRecording ? 'Stop' : 'Record 🎤'}
                                    </button>
                                <button
                                    onClick={clearTranscript}
                                    className="p-2.5 rounded-full hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-all duration-200 hover:rotate-180"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                                    </svg>
                                </button>
                                </div>
                            </div>
                            <div 
                                className="border rounded p-4 min-h-[300px] max-h-[500px] overflow-y-auto whitespace-pre-wrap"
                            >
                                {transcript.split('[highlight]').map((part, i) => {
                                    if (i === 0) return part;
                                    const [highlight, rest] = part.split('[/highlight]');
                                    return (
                                        <React.Fragment key={i}>
                                            <span 
                                                className="bg-yellow-200 px-1 rounded cursor-pointer"
                                                onMouseOver={(e) => handleMouseOver(e, highlight)}
                                                onMouseOut={handleMouseOut}
                                            >
                                                {highlight}
                                            </span>
                                            {rest}
                                        </React.Fragment>
                                    );
                                })}
                            </div>
                            {tooltipContent && (
                                <div 
                                    className="tooltip-content"
                                    style={{
                                        left: `${tooltipContent.x}px`,
                                        top: `${tooltipContent.y}px`,
                                        transform: 'translate(-50%, -100%)'
                                    }}
                                >
                                    {tooltipContent.text}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        }

        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>
'''

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return Markup(HTML_TEMPLATE)

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.get_json()
    text = data.get('text')
    keywords = data.get('keywords')
    if not text or not keywords:
        return jsonify({'error': 'Missing text or keywords'}), 400
    processed_text = correct_and_highlight_with_gpt4(text, keywords)
    return jsonify({'processed_text': processed_text})

@app.route('/get_definitions', methods=['POST'])
def get_definitions():
    try:
        data = request.get_json()
        keywords = data.get('keywords')
        if not keywords:
            return jsonify({'error': 'Missing keywords'}), 400
            
        definitions = create_dictionary_with_gpt4(keywords)
        
        if definitions is None:
            return jsonify({'error': 'Failed to generate definitions'}), 500
            
        return jsonify({'definitions': definitions})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True)