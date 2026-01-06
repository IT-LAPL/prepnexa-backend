FLASHCARD_GENERATOR_PROMPT = """
You are an expert teacher. 
Generate flashcards from the following text.
For each flashcard, provide:
- question
- answer
- difficulty (choose one of: easy, medium, hard)

Format the output strictly as JSON array, example:
[
    {{"question": "...", "answer": "...", "difficulty": "easy"}},
    ...
]

Text:
{context}
"""
