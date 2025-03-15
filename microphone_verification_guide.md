# Microphone Access Verification Guide

This guide helps you verify that your application is using real microphone input instead of simulation mode.

## Checking Microphone Access

When you start recording in the application, the browser will request permission to access your microphone. Make sure to allow this permission.

### Browser Console Logs

To verify that the application is using real microphone input, check the browser console logs:

1. Open your browser's developer tools:
   - Chrome: Press F12 or right-click > Inspect > Console
   - Firefox: Press F12 or right-click > Inspect Element > Console

2. Look for the following logs when you click "Start Recording":

```
Requesting microphone access for real transcription...
Microphone access granted, creating MediaRecorder
MediaRecorder started with 2000ms timeslice
Audio chunk received: [size] bytes
```

If you see these logs, the application is successfully using your physical microphone.

### Identifying Simulation Mode

If the application is using simulation mode, you'll see these logs instead:

```
ERROR: Microphone access denied or not available: [error details]
Falling back to simulation mode, but real microphone is recommended
```

You'll also see an alert message: "Microphone access is required for real transcription. Please allow microphone access and reload the page."

## Checking Audio Chunks

When using a real microphone, you should see log messages showing the size of each audio chunk:

```
Audio chunk received: 12345 bytes
```

The size will vary depending on your microphone and the duration of the recording, but it should be significantly larger than the dummy chunks used in simulation mode.

## Verifying Transcription

With real microphone input, the transcription should accurately reflect what you say, rather than showing the simulated text messages that appear in simulation mode.
