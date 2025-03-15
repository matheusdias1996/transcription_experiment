class AudioRecorder {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.stream = null;
    this.startTime = null;
    this.timerInterval = null;
    this.onDataAvailable = null; // Callback for real-time data
  }

  async startRecording(onDataAvailable) {
    try {
      // Try to get user media
      try {
        console.log('Requesting microphone access for real transcription...');
        this.stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          } 
        });
        
        console.log('Microphone access granted, creating MediaRecorder');
        this.mediaRecorder = new MediaRecorder(this.stream);
        
        this.audioChunks = [];
        this.isRecording = true;
        this.onDataAvailable = onDataAvailable;
        
        this.mediaRecorder.addEventListener('dataavailable', event => {
          console.log(`Audio chunk received: ${event.data.size} bytes`);
          this.audioChunks.push(event.data);
          
          // Call the callback with the latest chunk if provided
          if (this.onDataAvailable && event.data.size > 0) {
            this.onDataAvailable(event.data);
          }
        });
        
        // Start with timeslice of 2000ms (2 seconds) to avoid short audio chunks that cause "You" transcriptions
        this.mediaRecorder.start(2000);
        console.log('MediaRecorder started with 2000ms timeslice');
      } catch (mediaError) {
        console.error('ERROR: Microphone access denied or not available:', mediaError);
        alert('Microphone access is required for real transcription. Please allow microphone access and reload the page.');
        
        // We'll still set up a fallback, but alert the user that real mic is needed
        console.warn('Falling back to simulation mode, but real microphone is recommended');
        this.isRecording = true;
        this.onDataAvailable = onDataAvailable;
        
        // Create a simulation interval that sends dummy audio chunks
        this.simulationInterval = setInterval(() => {
          if (this.onDataAvailable) {
            // Create a small dummy audio blob (empty, just for testing)
            const dummyBlob = new Blob(['dummy audio data'], { type: 'audio/wav' });
            this.onDataAvailable(dummyBlob);
          }
        }, 2000); // Every 2 seconds
      }
      
      this.startTime = Date.now();
      return true;
    } catch (error) {
      console.error('Error starting recording:', error);
      return false;
    }
  }

  stopRecording() {
    return new Promise(resolve => {
      this.isRecording = false;
      
      // Clear simulation interval if it exists
      if (this.simulationInterval) {
        clearInterval(this.simulationInterval);
        this.simulationInterval = null;
        resolve(new Blob(['dummy audio data'], { type: 'audio/wav' }));
        return;
      }
      
      // Handle real MediaRecorder
      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
        resolve(null);
        return;
      }

      this.mediaRecorder.addEventListener('stop', () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });

        // Stop all tracks
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
        }

        resolve(audioBlob);
      });

      this.mediaRecorder.stop();
    });
  }

  formatTime(ms) {
    const seconds = Math.floor((ms / 1000) % 60);
    const minutes = Math.floor((ms / (1000 * 60)) % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }

  startTimer(updateCallback) {
    this.timerInterval = setInterval(() => {
      const elapsedTime = Date.now() - this.startTime;
      updateCallback(this.formatTime(elapsedTime));
    }, 1000);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }
}                