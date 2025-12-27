import re
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processed_text import ProcessedText
from app.models.upload import Upload
from app.models.question import Question
from app.models.question_topic import QuestionTopic
from app.models.exam import Subject, Topic

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Regex to catch questions like 1. Text, 2) Text etc.
QUESTION_REGEX = r"(?:^|\n)(\d{1,2}[.)]\s+.*?)(?=\n\d{1,2}[.)]\s+|\Z)"


async def extract_questions(
    db: AsyncSession,
    upload: Upload,
    processed_text: ProcessedText,
):
    logger.info(f"📝 Extracting questions from processed_text_id={processed_text.id}")

    text = processed_text.cleaned_text
    matches = re.findall(QUESTION_REGEX, text, re.DOTALL)

    if not matches:
        logger.warning("⚠️ No questions found in processed text")
        return

    logger.info(f"Found {len(matches)} questions in processed text")

    for idx, q_text in enumerate(matches, start=1):
        q_text_cleaned = q_text.strip()

        question = Question(
            processed_text_id=processed_text.id,
            exam_id=upload.exam_id,
            subject_id="50288f34-0039-4703-a2c0-95a4299a6fe3",  # update to correct subject_id if available
            year=upload.year,
            question_number=idx,
            question_text=q_text_cleaned,
        )
        db.add(question)
        await db.flush()  # get ID

        # Optional: assign topics if topics exist for this subject
        stmt = (
            select(Topic)
            .join(Topic.subject)  # join Topic → Subject
            .where(Subject.exam_id == upload.exam_id)
        )
        result = await db.execute(stmt)
        topics = result.scalars().all()

        for topic in topics:
            if topic.name.lower() in q_text_cleaned.lower():
                q_topic = QuestionTopic(
                    question_id=question.id,
                    topic_id=topic.id,
                    confidence=1.0,  # naive assignment
                )
                db.add(q_topic)
                logger.info(f"✅ Assigned topic '{topic.name}' to question {idx}")

    await db.commit()
    logger.info(f"🎯 Extraction complete for processed_text_id={processed_text.id}")
