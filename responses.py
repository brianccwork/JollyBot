import random
import os
import openai
import logging

logging.basicConfig(level=logging.INFO)

def get_response_ai(user_input: str) -> str:
    openai.api_key = os.getenv('OPENAI_API_KEY')  # Ensure your API key is loaded correctly
    try:
        logging.info(f"Sending prompt to OpenAI: {user_input}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a cheerful Christmas assistant."},
                {"role": "user", "content": user_input},
            ],
            max_tokens=50
        )
        logging.info(f"OpenAI Response: {response['choices'][0]['message']['content'].strip()}")
        return response["choices"][0]["message"]["content"].strip()
    except openai.OpenAIError as e:
        logging.error(f"Error in OpenAI API call: {e}")
        return "I'm having some trouble reaching the North Pole. Please try again later!"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "Oops, I'm feeling less jolly right now. Try again later!"
