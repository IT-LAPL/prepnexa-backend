import json
import logging
from typing import List

from app.repositories.flashcard_repo import FlashcardRepository
from app.services.llm_client import call_llm
from app.models.flashcards import Flashcard, FlashcardDifficulty

logger = logging.getLogger(__name__)


class FlashcardService:
    def __init__(self, repo: FlashcardRepository):
        self.repo = repo

    async def generate_flashcards(
        self, user_id: str, predicted_paper_id: str, text: str, max_cards: int = 20
    ) -> List[Flashcard]:
        """Generate flashcards from `text` using the LLM and persist them.

        Returns the list of created `Flashcard` objects.
        """
        if not text or not text.strip():
            logger.info("No text provided for flashcard generation")
            return []

        prompt = (
            "Generate up to {n} concise question-answer flashcards from the following "
            "exam content. Return a JSON array of objects with keys: 'question', 'answer', "
            "and 'difficulty' (one of 'easy','medium','hard'). Only output valid JSON.\n\n"
        ).format(n=max_cards)
        prompt += text[:15000]

        logger.info("Requesting flashcard generation from LLM (max %d)", max_cards)
        resp = await call_llm(prompt)

        cards = []
        if not resp or not resp.strip():
            logger.warning("LLM returned empty response for flashcard generation")
            return []

        # attempt to parse JSON; tolerate surrounding text or markdown
        def _extract_json_substring(s: str):
            # strip common markdown code fences
            if s.strip().startswith("```") and s.strip().endswith("```"):
                # remove leading/trailing code fences
                parts = s.strip().split("```")
                # parts may be ['', 'json\n[...',''] or similar
                if len(parts) >= 2:
                    s = "```".join(parts[1:-1])

            # find first JSON opening brace/bracket
            for open_ch, close_ch in (("[", "]"), ("{", "}")):
                start = s.find(open_ch)
                if start == -1:
                    continue
                depth = 0
                in_str = False
                esc = False
                for i in range(start, len(s)):
                    ch = s[i]
                    if ch == '"' and not esc:
                        in_str = not in_str
                    if in_str and ch == "\\" and not esc:
                        esc = True
                        continue
                    if not in_str:
                        if ch == open_ch:
                            depth += 1
                        elif ch == close_ch:
                            depth -= 1
                            if depth == 0:
                                try:
                                    return s[start : i + 1]
                                except Exception:
                                    return None
                    if esc:
                        esc = False
            return None

        data = None
        try:
            data = json.loads(resp)
        except Exception:
            # try extracting a JSON substring
            substr = _extract_json_substring(resp)
            if substr:
                try:
                    data = json.loads(substr)
                except Exception:
                    data = None

        if isinstance(data, list):
            for item in data[:max_cards]:
                q = item.get("question")
                a = item.get("answer")
                d = item.get("difficulty", "medium")
                if not q or not a:
                    continue
                try:
                    difficulty = FlashcardDifficulty(d)
                except Exception:
                    difficulty = FlashcardDifficulty.medium

                fc = Flashcard(
                    user_id=user_id,
                    predicted_paper_id=predicted_paper_id,
                    question=q.strip(),
                    answer=a.strip(),
                    difficulty=difficulty,
                )
                await self.repo.create(fc)
                cards.append(fc)
        else:
            # fallback: parse lines of 'Q: ... \n A: ...' pairs
            logger.info("No JSON list parsed; falling back to line parsing")
            lines = [l.strip() for l in resp.splitlines() if l.strip()]
            i = 0
            while i < len(lines) - 1 and len(cards) < max_cards:
                line = lines[i]
                if line.lower().startswith("q:"):
                    question = line[2:].strip()
                    answer = ""
                    if i + 1 < len(lines) and lines[i + 1].lower().startswith("a:"):
                        answer = lines[i + 1][2:].strip()
                        i += 2
                    else:
                        i += 1
                    if question and answer:
                        fc = Flashcard(
                            user_id=user_id,
                            predicted_paper_id=predicted_paper_id,
                            question=question,
                            answer=answer,
                            difficulty=FlashcardDifficulty.medium,
                        )
                        await self.repo.create(fc)
                        cards.append(fc)
                else:
                    i += 1

        # commit once after creating all
        await self.repo.db.commit()
        logger.info(
            "Created %d flashcards for predicted_paper=%s",
            len(cards),
            predicted_paper_id,
        )
        return cards
