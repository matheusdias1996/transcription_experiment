# Troubleshooting Guide for Microphone Access and Transcription

If you're experiencing issues with microphone access or transcription quality, this guide provides solutions to common problems.

## Microphone Access Issues

### Problem: Browser shows "Microphone access denied" error

**Solutions:**

1. **Check browser permissions:**
   - Click the lock/info icon in your browser's address bar
   - Ensure microphone access is allowed for localhost
   - If denied, change to "Allow" and reload the page

2. **Reset browser permissions:**
   - Chrome: Settings > Privacy and security > Site Settings > Microphone
   - Firefox: Settings > Privacy & Security > Permissions > Microphone
   - Clear any blocked settings for localhost

3. **Try a different browser:**
   - Chrome and Firefox generally have good support for the MediaRecorder API
   - Edge and Safari may have different permission models

### Problem: "Requested device not found" error

**Solutions:**

1. **Check physical connections:**
   - Ensure your microphone is properly connected to your computer
   - Try a different USB port if using an external microphone

2. **Check system settings:**
   - Verify your microphone is set as the default input device in your operating system
   - Check that the microphone is not muted or disabled

3. **Test microphone in another application:**
   - Use a simple recording app or online microphone test to verify your microphone works

## Transcription Issues

### Problem: Transcription shows "You you you" or incorrect text

**Solutions:**

1. **Check audio chunk size:**
   - The application is configured to use 2000ms chunks to avoid the "You" issue
   - Verify in the browser console that chunks are being sent with sufficient size

2. **Check OpenAI API key:**
   - Ensure your OpenAI API key is correctly set in the .env file
   - Verify the API key has access to the Whisper API

3. **Check network connectivity:**
   - Ensure you have a stable internet connection
   - The OpenAI API requires internet access for transcription

### Problem: No transcription appears at all

**Solutions:**

1. **Check browser console for errors:**
   - Look for any error messages related to transcription
   - API errors will be displayed in the console

2. **Verify backend server is running:**
   - Ensure the backend server is running on port 5000
   - Check for any error messages in the terminal where you started the server

3. **Check WebSocket connection:**
   - Look for "Connected to server" message in the console
   - If disconnected, try reloading the page

## OpenAI API Issues

### Problem: "API key is missing or invalid" error

**Solutions:**

1. **Check .env file:**
   - Ensure the .env file exists in the root directory
   - Verify the format is exactly: `OPENAI_API_KEY=your_key_here`
   - No quotes or spaces around the key

2. **Verify API key validity:**
   - Check that your OpenAI API key is active and has sufficient credits
   - Try the key in another OpenAI API application to verify it works

3. **Restart the server:**
   - Stop the application (Ctrl+C in the terminal)
   - Start it again with `npm start`
   - The server needs to be restarted after changing the .env file

### Problem: "The audio file could not be decoded" error

**Solutions:**

1. **Check audio format:**
   - The application should be sending properly formatted WAV audio
   - Verify the audio chunk processing in the browser console

2. **Try speaking more clearly:**
   - Ensure you're speaking at a reasonable volume
   - Reduce background noise

3. **Try a different microphone:**
   - Some microphones may produce audio that's difficult for the API to process
   - External microphones often provide better quality than built-in ones
