class AudioRecorder {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.stream = null;
    this.startTime = null;
    this.timerInterval = null;
  }

  async startRecording() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(this.stream);

      this.audioChunks = [];
      this.isRecording = true;

      this.mediaRecorder.addEventListener('dataavailable', event => {
        this.audioChunks.push(event.data);
      });

      this.mediaRecorder.start();
      this.startTime = Date.now();

      return true;
    } catch (error) {
      console.error('Error starting recording:', error);
      return false;
    }
  }

  stopRecording() {
    return new Promise(resolve => {
      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
        resolve(null);
        return;
      }

      this.mediaRecorder.addEventListener('stop', () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        this.isRecording = false;

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