describe('AudioRecorder', () => {
  let AudioRecorder;

  beforeEach(() => {
    // Mock the MediaRecorder and getUserMedia
    global.MediaRecorder = jest.fn().mockImplementation(() => ({
      start: jest.fn(),
      stop: jest.fn(),
      addEventListener: jest.fn((event, callback) => {
        if (event === 'stop') {
          setTimeout(() => callback(), 10);
        }
      }),
      state: 'inactive'
    }));

    global.navigator.mediaDevices = {
      getUserMedia: jest.fn().mockResolvedValue({
        getTracks: jest.fn().mockReturnValue([{ stop: jest.fn() }])
      })
    };

    // Import the AudioRecorder class
    jest.isolateModules(() => {
      AudioRecorder = require('../scripts/recorder').AudioRecorder;
    });
  });

  test('startRecording should initialize MediaRecorder', async () => {
    const recorder = new AudioRecorder();
    const result = await recorder.startRecording();

    expect(result).toBe(true);
    expect(recorder.isRecording).toBe(true);
    expect(global.MediaRecorder).toHaveBeenCalled();
  });

  test('stopRecording should return an audio blob', async () => {
    const recorder = new AudioRecorder();
    await recorder.startRecording();

    global.Blob = jest.fn().mockImplementation(() => 'test-blob');

    const result = await recorder.stopRecording();
    expect(result).toBe('test-blob');
    expect(recorder.isRecording).toBe(false);
  });

  test('formatTime should format milliseconds correctly', () => {
    const recorder = new AudioRecorder();
    expect(recorder.formatTime(65000)).toBe('01:05');
    expect(recorder.formatTime(3661000)).toBe('61:01');
  });
});