import re
import logging
from typing import Optional

from app.models.processed_text import ProcessedText
from app.models.upload import Upload
from app.repositories.question_repo import QuestionRepository
from app.repositories.topic_repo import TopicRepository

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Regex to catch questions like 1. Text, 2) Text etc.
QUESTION_REGEX = r"(?:^|\n)(\d{1,2}[.)]\s+.*?)(?=\n\d{1,2}[.)]\s+|\Z)"


class QuestionExtractorService:
    def __init__(self, question_repo: QuestionRepository, topic_repo: TopicRepository):
        self.question_repo = question_repo
        self.topic_repo = topic_repo

    async def extract_questions(self, upload: Upload, processed_text: ProcessedText):
        logger.info(
            f"📝 Extracting questions from processed_text_id={processed_text.id}"
        )

        text = processed_text.cleaned_text
        matches = re.findall(QUESTION_REGEX, text, re.DOTALL)

        if not matches:
            logger.warning("⚠️ No questions found in processed text")
            return

        logger.info(f"Found {len(matches)} questions in processed text")

        # get topics for this exam once
        topics = await self.topic_repo.list_topics_by_exam(upload.exam_id)

        for idx, q_text in enumerate(matches, start=1):
            q_text_cleaned = q_text.strip()

            # TODO: determine proper subject_id for the question; using None placeholder
            question = await self.question_repo.create_question(
                processed_text_id=processed_text.id,
                exam_id=upload.exam_id,
                subject_id="50288f34-0039-4703-a2c0-95a4299a6fe3",
                year=upload.year,
                question_number=idx,
                question_text=q_text_cleaned,
            )

            for topic in topics:
                if topic.name.lower() in q_text_cleaned.lower():
                    await self.question_repo.add_question_topic(
                        question_id=question.id, topic_id=topic.id, confidence=1.0
                    )
                    logger.info(f"✅ Assigned topic '{topic.name}' to question {idx}")

        # let caller commit when appropriate
        logger.info(f"🎯 Extraction staged for processed_text_id={processed_text.id}")
