# Local Testing Guide for Transcription Experiment

This guide provides instructions for testing the transcription application locally with a physical microphone to verify the real-time transcription functionality.

## Prerequisites

- Git installed on your local machine
- Node.js and npm installed
- A physical microphone connected to your computer
- An OpenAI API key

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/matheusdias1996/transcription_experiment.git
cd transcription_experiment
```

### 2. Checkout the Feature Branch

```bash
git checkout devin/1742026224-real-time-qna
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory of the project and add your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual OpenAI API key.

### 5. Start the Application

```bash
npm start
```

This command will start both the frontend and backend servers:
- Frontend: http://localhost:8000/
- Backend: http://localhost:5000/

### 6. Access the Application

Open your web browser and navigate to:

```
http://localhost:8000/
```

You should see the Voice Recorder & Question Answering interface.
