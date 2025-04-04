document.addEventListener('DOMContentLoaded', () => {
  const recordButton = document.getElementById('recordButton');
  const recordingStatus = document.getElementById('recordingStatus');
  const recordingTime = document.getElementById('recordingTime');
  const transcriptionOutput = document.getElementById('transcriptionOutput');
  const questionInput = document.getElementById('questionInput');
  const askButton = document.getElementById('askButton');
  const answerOutput = document.getElementById('answerOutput');
  const translateToLanguage = document.getElementById('translateToLanguage');

  const recorder = new AudioRecorder();
  let currentTranscription = '';
  let originalTranscription = '';

  // Add event listener for language selection change
  translateToLanguage.addEventListener('change', async () => {
    console.log('Language changed to:', translateToLanguage.value);
    if (currentTranscription) {
      await translateTranscription();
    }
  });

  // Function to translate existing transcription
  async function translateTranscription() {
    const selectedLanguage = translateToLanguage.value;
    
    // If no language is selected, revert to original transcription
    if (!selectedLanguage) {
      transcriptionOutput.textContent = originalTranscription || currentTranscription;
      recordingStatus.textContent = 'Transcription complete';
      return;
    }
    
    try {
      recordingStatus.textContent = 'Translating...';
      
      const response = await fetch('http://127.0.0.1:5000/api/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: originalTranscription || currentTranscription,
          target_language: selectedLanguage
        })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server responded with ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        recordingStatus.textContent = `Error: ${data.error}`;
        console.error('Translation error:', data.error);
        return;
      }
      
      currentTranscription = data.translation;
      transcriptionOutput.textContent = currentTranscription;
      
      const languageName = translateToLanguage.options[translateToLanguage.selectedIndex].text;
      recordingStatus.textContent = `Transcription translated to ${languageName}`;
      
    } catch (error) {
      console.error('Error translating text:', error);
      recordingStatus.textContent = `Error: ${error.message}. Check console for details.`;
    }
  }

  // Recording functionality
  recordButton.addEventListener('click', async () => {
    if (!recorder.isRecording) {
      // Start recording
      recordingStatus.textContent = 'Recording...';
      recordButton.textContent = 'Stop Recording';
      recordButton.classList.add('recording');

      const success = await recorder.startRecording();
      if (success) {
        recorder.startTimer(time => {
          recordingTime.textContent = time;
        });
      } else {
        recordingStatus.textContent = 'Failed to start recording';
        recordButton.textContent = 'Start Recording';
        recordButton.classList.remove('recording');
      }
    } else {
      // Stop recording
      recordingStatus.textContent = 'Processing...';
      recordButton.textContent = 'Start Recording';
      recordButton.classList.remove('recording');
      recorder.stopTimer();

      const audioBlob = await recorder.stopRecording();
      if (audioBlob) {
        await transcribeAudio(audioBlob);
      } else {
        recordingStatus.textContent = 'No recording to process';
      }
    }
  });

  // Transcription functionality
  async function transcribeAudio(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);

    try {
      recordingStatus.textContent = 'Connecting to server...';

      const response = await fetch('http://127.0.0.1:5000/api/transcribe', {
        method: 'POST',
        body: formData
      });

      recordingStatus.textContent = 'Processing response...';

      // Check if the response is ok before trying to parse JSON
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server responded with ${response.status}: ${errorText}`);
      }

      const data = await response.json();

      if (data.error) {
        recordingStatus.textContent = `Error: ${data.error}`;
        console.error('Transcription error:', data.error);
        return;
      }

      originalTranscription = data.transcription;
      currentTranscription = data.transcription;
      transcriptionOutput.textContent = currentTranscription;
      recordingStatus.textContent = 'Transcription complete';

    } catch (error) {
      console.error('Error transcribing audio:', error);
      recordingStatus.textContent = `Error: ${error.message}. Check console for details.`;
    }
  }

  // Question answering functionality
  askButton.addEventListener('click', async () => {
    const question = questionInput.value.trim();

    if (!question) {
      answerOutput.textContent = 'Please enter a question';
      return;
    }

    if (!currentTranscription) {
      answerOutput.textContent = 'No transcription available. Record something first.';
      return;
    }

    answerOutput.textContent = 'Thinking...';

    try {
      const response = await fetch('http://127.0.0.1:5000/api/question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: question,
          transcription: currentTranscription
        })
      });

      // Check if the response is ok before trying to parse JSON
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server responded with ${response.status}: ${errorText}`);
      }

      const data = await response.json();

      if (data.error) {
        answerOutput.textContent = `Error: ${data.error}`;
        return;
      }

      answerOutput.textContent = data.answer;

    } catch (error) {
      console.error('Error getting answer:', error);
      answerOutput.textContent = `Error: ${error.message}. Check console for details.`;
    }
  });
});         