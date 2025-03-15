# Transcription Experiment

A web application for real-time voice recording, transcription, and question answering.

## Features

- Real-time audio transcription while recording
- Ask questions about the transcription while recording continues
- Get real-time answers to questions as you speak
- Translate transcriptions to multiple languages

## Setup

1. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```
   npm install
   ```

3. Create a `.env` file in the backend directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Development

Start both frontend and backend servers:
```
npm start
```

## How it works

- The application uses WebSockets for real-time communication between the frontend and backend
- Audio is recorded in chunks and sent to the backend for processing
- Transcription is updated in real-time as you speak
- Questions can be asked at any time and answers are streamed back in real-time
- Translation functionality allows switching between multiple languages
