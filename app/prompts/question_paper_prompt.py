# app/prompts/question_paper_prompt.py

QUESTION_PAPER_PROMPT = """
You are an expert exam paper setter for Indian school examinations.

Using the PREVIOUS YEAR QUESTION PAPER TEXT below,
generate a NEW QUESTION PAPER with:

- Same exam pattern
- Same difficulty level
- Same section structure
- New questions (do NOT repeat questions)
- Balanced coverage of topics

Format:
- Section A (MCQs / 1 mark)
- Section B (2 marks)
- Section C (3 marks)
- Section D (5 marks)

PREVIOUS QUESTION PAPER:
------------------------
{context}
------------------------

Generate the NEW QUESTION PAPER now:
"""
