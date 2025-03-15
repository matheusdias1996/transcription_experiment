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
        this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(this.stream);
        
        this.audioChunks = [];
        this.isRecording = true;
        this.onDataAvailable = onDataAvailable;
        
        this.mediaRecorder.addEventListener('dataavailable', event => {
          this.audioChunks.push(event.data);
          
          // Call the callback with the latest chunk if provided
          if (this.onDataAvailable && event.data.size > 0) {
            this.onDataAvailable(event.data);
          }
        });
        
        // Start with timeslice of 1000ms (1 second) to get frequent chunks
        this.mediaRecorder.start(1000);
      } catch (mediaError) {
        console.warn('Media device not available, using simulation mode:', mediaError);
        
        // Simulate recording with dummy data in environments without microphone access
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