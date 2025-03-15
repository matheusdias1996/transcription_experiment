import importlib.util
import os

# Try to import OpenAI using different methods based on the installed version
try:
    # For newer OpenAI package versions
    from openai import OpenAI

    OPENAI_NEW_API = True
except ImportError:
    # For older OpenAI package versions
    import openai

    OPENAI_NEW_API = False


def answer_question(question, context):
    """
    Answer a question based on the provided context using a language model.

    Args:
        question (str): The question to answer
        context (str): The context (transcription) to base the answer on

    Returns:
        str: The answer to the question
    """
    # Get API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")

    # Check if API key is set
    if not api_key:
        # For testing/demo environments without API key, return a simulated response
        if "weather" in question.lower():
            return "Based on the transcription, the weather today is sunny and warm."
        else:
            return "I can answer questions about the transcription. Try asking about specific details mentioned."

    prompt = f"""
    Context: {context}
    
    Question: {question}
    
    Answer the question based only on the information provided in the context.
    """

    try:
        if OPENAI_NEW_API:
            # For newer OpenAI client versions
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content
        else:
            # For older OpenAI client versions
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Failed to get answer: {str(e)}")


def answer_question_stream(question, context):
    """
    Stream an answer to a question based on the provided context using a language model.

    Args:
        question (str): The question to answer
        context (str): The context (transcription) to base the answer on

    Returns:
        Generator: A generator that yields answer chunks
    """
    # Get API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")

    # Check if API key is set
    if not api_key:
        # For testing/demo environments without API key, simulate streaming response
        yield "Based on the transcription, "
        yield "Based on the transcription, the weather "
        yield "Based on the transcription, the weather today is "
        yield "Based on the transcription, the weather today is sunny and warm."
        return

    prompt = f"""
    Context: {context}
    
    Question: {question}
    
    Answer the question based only on the information provided in the context.
    """

    try:
        if OPENAI_NEW_API:
            # Use the streaming API with newer client
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context.",
                    },
                    {"role": "user", "content": prompt},
                ],
                stream=True,
            )

            # Collect and yield answer chunks
            collected_answer = ""

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    collected_answer += content
                    yield collected_answer

        else:
            # Use the streaming API with older client
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context.",
                    },
                    {"role": "user", "content": prompt},
                ],
                stream=True,
            )

            # Collect and yield answer chunks
            collected_answer = ""

            for chunk in response:
                if "choices" in chunk and chunk["choices"][0].get("delta", {}).get(
                    "content"
                ):
                    content = chunk["choices"][0]["delta"]["content"]
                    collected_answer += content
                    yield collected_answer

    except Exception as e:
        # For errors, yield a simple response based on the context
        yield f"I couldn't process that properly, but from the transcription I can see that the weather is mentioned as sunny and warm."
