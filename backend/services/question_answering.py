import openai
import os

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
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Check if API key is set
    if not openai.api_key:
        raise ValueError("OpenAI API key is not set in environment variables")
    
    prompt = f"""
    Context: {context}
    
    Question: {question}
    
    Answer the question based only on the information provided in the context.
    """
    
    try:
        # Try the newer client first
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fall back to older client
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to get answer: {str(e)}") 