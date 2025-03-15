"""
Check environment variables and dependencies for the transcription experiment.
"""
import os
import sys


def check_environment():
    """Check environment variables and dependencies."""
    print("=== Environment Check ===")

    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"OPENAI_API_KEY set: {bool(api_key)}")
    if api_key:
        print(f"API key starts with: {api_key[:4]}... and ends with: ...{api_key[-4:]}")

    # Check Python version
    print(f"Python version: {sys.version}")

    # Check required modules
    modules_to_check = [
        "flask",
        "flask_socketio",
        "openai",
        "wave",
        "numpy",
        "base64",
        "io",
        "dotenv",
        "httpx",
    ]

    print("\n=== Module Availability ===")
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"{module}: Available")
        except ImportError:
            print(f"{module}: Not available")

    # Check OpenAI version
    try:
        import openai

        print(f"\nOpenAI version: {openai.__version__}")
    except (ImportError, AttributeError):
        print("\nCould not determine OpenAI version")


if __name__ == "__main__":
    check_environment()
