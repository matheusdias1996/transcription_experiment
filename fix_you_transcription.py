"""
Script to diagnose and fix the "You you you" transcription issue.
This script checks for common issues and provides solutions.
"""
import os
import sys
import time
from pathlib import Path


def check_openai_key():
    """Check if OpenAI API key is set and valid."""
    print("=== Checking OpenAI API Key ===")

    # Check environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable is not set!")
        print("This is likely the cause of the 'You you you' transcription issue.")

        # Check for .env file
        env_path = Path(".env")
        if not env_path.exists():
            print("❌ No .env file found in the project root.")
            print("\nTo fix this issue:")
            print("1. Create a .env file in the project root with:")
            print("   OPENAI_API_KEY=your_key_here")
            print("2. Restart the application to load the new environment variable")
            return False
        else:
            print(
                "✅ .env file exists, but OPENAI_API_KEY might not be set correctly in it."
            )
            print("Check the contents of your .env file.")
            return False
    else:
        print(f"✅ OPENAI_API_KEY is set: {api_key[:4]}...{api_key[-4:]}")

        # Validate key format (basic check)
        if not api_key.startswith("sk-") or len(api_key) < 20:
            print(
                "⚠️ API key format looks suspicious. Should start with 'sk-' and be longer."
            )
            return False

        print("✅ API key format looks valid.")
        return True


def check_audio_processing():
    """Check audio processing configuration."""
    print("\n=== Checking Audio Processing ===")

    # Check if wave module is available
    try:
        import wave

        print("✅ wave module is available for WAV file handling")
    except ImportError:
        print("❌ wave module is not available!")
        print("Install it with: pip install wave")
        return False

    # Check if numpy is available (optional but helpful)
    try:
        import numpy

        print("✅ numpy is available for audio processing")
    except ImportError:
        print(
            "⚠️ numpy is not available. Some audio processing features may be limited."
        )
        print("Install it with: pip install numpy")

    # Check if httpx is available (needed for OpenAI client)
    try:
        import httpx

        print("✅ httpx is available for OpenAI client")
    except ImportError:
        print("❌ httpx is not available!")
        print("Install it with: pip install httpx")
        return False

    # Check OpenAI package version
    try:
        import openai

        print(f"✅ OpenAI package version: {openai.__version__}")
    except (ImportError, AttributeError):
        print("❌ OpenAI package not available or version info missing!")
        print("Install it with: pip install openai")
        return False

    return True


def check_frontend_backend_communication():
    """Check frontend-backend communication."""
    print("\n=== Checking Frontend-Backend Communication ===")

    # Check if Flask-SocketIO is available
    try:
        import flask_socketio

        print("✅ Flask-SocketIO is available for WebSocket communication")
    except ImportError:
        print("❌ Flask-SocketIO is not available!")
        print("Install it with: pip install flask-socketio")
        return False

    # Check if eventlet is available
    try:
        import eventlet

        print("✅ eventlet is available for WebSocket support")
    except ImportError:
        print("❌ eventlet is not available!")
        print("Install it with: pip install eventlet")
        return False

    return True


def check_backend_running():
    """Check if backend server is running."""
    print("\n=== Checking Backend Server ===")

    import socket

    # Try to connect to the backend server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", 5000))
        s.close()
        print("✅ Backend server is running on port 5000")
        return True
    except (socket.error, socket.timeout):
        print("❌ Backend server is not running on port 5000!")
        print("Start the server with: python backend/app.py")
        return False


def fix_env_file():
    """Create or update .env file with OpenAI API key."""
    print("\n=== Creating/Updating .env File ===")

    # Ask for API key
    print("Enter your OpenAI API key (starts with 'sk-'):")
    api_key = input("> ")

    if not api_key:
        print("❌ No API key provided. Skipping .env file creation.")
        return False

    # Basic validation
    if not api_key.startswith("sk-") or len(api_key) < 20:
        print(
            "⚠️ API key format looks suspicious. Should start with 'sk-' and be longer."
        )
        print("Continue anyway? (y/n)")
        if input("> ").lower() != "y":
            return False

    # Create or update .env file
    with open(".env", "w") as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")

    print("✅ Created/updated .env file with API key")
    print("⚠️ You need to restart the application for changes to take effect")
    return True


def main():
    """Main function to diagnose and fix issues."""
    print("=== 'You you you' Transcription Issue Diagnostic Tool ===")
    print("This tool will help diagnose and fix the issue where transcription")
    print("only shows 'You you you' regardless of what is said.\n")

    # Check for issues
    key_ok = check_openai_key()
    audio_ok = check_audio_processing()
    comm_ok = check_frontend_backend_communication()
    server_ok = check_backend_running()

    # Summarize findings
    print("\n=== Diagnosis Summary ===")
    if not key_ok:
        print("❌ OpenAI API key issue detected - HIGHEST PRIORITY")
    if not audio_ok:
        print("❌ Audio processing issue detected")
    if not comm_ok:
        print("❌ Frontend-backend communication issue detected")
    if not server_ok:
        print("❌ Backend server is not running")

    if key_ok and audio_ok and comm_ok and server_ok:
        print("✅ All checks passed! If you're still seeing 'You you you',")
        print("   the issue might be with the audio recording quality or content.")

    # Offer fixes
    print("\n=== Recommended Fixes ===")

    if not key_ok:
        print("1. Fix OpenAI API key issue (recommended)")
    if not server_ok:
        print("2. Start the backend server")
    if not audio_ok or not comm_ok:
        print("3. Install missing dependencies")

    print("\nWhich issue would you like to fix? (Enter number, or 0 to exit)")
    choice = input("> ")

    if choice == "1" or (not key_ok and choice == ""):
        fix_env_file()
        print("\nAfter fixing the API key:")
        print("1. Restart the backend server: python backend/app.py")
        print("2. Refresh the frontend page in your browser")
    elif choice == "2":
        print("\nTo start the backend server:")
        print("1. Open a terminal in the project root")
        print("2. Run: python backend/app.py")
    elif choice == "3":
        print("\nTo install missing dependencies:")
        print("1. Open a terminal in the project root")
        print("2. Run: pip install -r requirements.txt")
    else:
        print("\nExiting without making changes.")

    print("\nDiagnostic complete. If issues persist after applying fixes,")
    print("run the test_audio_with_key.py script for more detailed testing.")


if __name__ == "__main__":
    main()
