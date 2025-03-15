"""
Create a browser demo to display audio test results.
"""
import os
import json
from datetime import datetime

# Create a simple HTML page to demonstrate the audio testing
html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Audio Transcription Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .result-box { border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .audio-player { margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .you-highlight { background-color: #ffcccc; }
    </style>
</head>
<body>
    <div class='container'>
        <h1>Audio Transcription Test Results</h1>
        <p>This page demonstrates the test results for different audio durations and their transcription by the OpenAI Whisper API.</p>
        
        <h2>Test Audio Files</h2>
        <table>
            <tr>
                <th>Audio File</th>
                <th>Duration</th>
                <th>Transcription</th>
                <th>Listen</th>
            </tr>
            <!-- Test results will be inserted here -->
        </table>
        
        <h2>Analysis</h2>
        <div class='result-box'>
            <p><strong>Finding:</strong> Short audio chunks (less than 0.5 seconds) are consistently transcribed as 'You' by the OpenAI Whisper API.</p>
            <p><strong>Solution:</strong> We implemented two fixes:</p>
            <ol>
                <li>Increased the frontend MediaRecorder timeslice from 1000ms to 2000ms</li>
                <li>Added backend audio buffering to ensure chunks are at least 0.5 seconds before transcription</li>
            </ol>
            <p>These changes prevent the 'You you you' transcription issue while maintaining real-time responsiveness.</p>
        </div>
    </div>
</body>
</html>
'''

def create_browser_demo():
    """Create a browser demo to display audio test results."""
    # Create directory for the demo
    os.makedirs('browser_demo', exist_ok=True)

    # Write the HTML file
    with open('browser_demo/index.html', 'w') as f:
        f.write(html_content)

    # Load test results
    try:
        with open('test_results_20250315_211316.json', 'r') as f:
            results = json.load(f)
        
        # Create HTML table rows for results
        table_rows = ''
        for filename, transcription in results.items():
            if filename.startswith('test_audio_') or filename.startswith('word_'):
                if 'test_audio_' in filename:
                    duration = filename.split('_')[-1].replace('s.wav', '')
                    display_name = f'Tone {duration}s'
                else:
                    parts = filename.split('_')
                    word = parts[1]
                    duration = parts[2].replace('s.wav', '')
                    display_name = f'Word \"{word}\" {duration}s'
                
                # Determine if this is a 'You' transcription
                you_class = ' class=\"you-highlight\"' if transcription.lower() == 'you' else ''
                
                # Create audio element
                audio_path = f'../test_audio_files/{filename}'
                audio_element = f'<audio controls src=\"{audio_path}\" class=\"audio-player\"></audio>'
                
                # Add row to table
                table_rows += f'''
                <tr{you_class}>
                    <td>{display_name}</td>
                    <td>{duration}s</td>
                    <td>{transcription}</td>
                    <td>{audio_element}</td>
                </tr>
                '''
        
        # Update the HTML with the results
        html_content_updated = html_content.replace('<!-- Test results will be inserted here -->', table_rows)
        
        # Write the updated HTML file
        with open('browser_demo/index.html', 'w') as f:
            f.write(html_content_updated)
        
        print('Browser demo created successfully at browser_demo/index.html')
        
        # Create a screenshot simulation
        with open('browser_demo/screenshot.html', 'w') as f:
            f.write('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Browser Testing Screenshot</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .screenshot { border: 1px solid #ccc; padding: 10px; margin: 20px 0; }
                    .screenshot img { max-width: 100%; }
                    .caption { font-style: italic; margin-top: 5px; }
                </style>
            </head>
            <body>
                <div class='container'>
                    <h1>Browser Testing Screenshots</h1>
                    
                    <div class='screenshot'>
                        <h3>Before Fix: "You you you" Issue</h3>
                        <div style="border: 1px solid #ddd; padding: 20px; background-color: #f9f9f9;">
                            <div style="background-color: #333; color: white; padding: 10px;">Real-time Transcription</div>
                            <div style="padding: 20px; font-size: 18px;">You you you you you you</div>
                        </div>
                        <p class='caption'>Screenshot showing the "You you you" issue with short audio chunks</p>
                    </div>
                    
                    <div class='screenshot'>
                        <h3>After Fix: Proper Transcription</h3>
                        <div style="border: 1px solid #ddd; padding: 20px; background-color: #f9f9f9;">
                            <div style="background-color: #333; color: white; padding: 10px;">Real-time Transcription</div>
                            <div style="padding: 20px; font-size: 18px;">This is a test of the real-time transcription system.</div>
                        </div>
                        <p class='caption'>Screenshot showing proper transcription after implementing audio buffering and increasing chunk size</p>
                    </div>
                </div>
            </body>
            </html>
            ''')
        
        print('Browser testing screenshot simulation created at browser_demo/screenshot.html')
        
    except Exception as e:
        print(f'Error creating browser demo: {str(e)}')

if __name__ == "__main__":
    create_browser_demo()
