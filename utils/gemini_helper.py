import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

def get_ai_response(prompt):

    response = model.generate_content(
        f"""
        You are an AI Study Buddy.

        Explain concepts in simple language.

        Generate:
        - Notes
        - Summaries
        - Flashcards
        - Quizzes

        User Question:
        {prompt}
        """
    )

    return response.text