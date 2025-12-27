from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from collections import defaultdict

from app.models.question import Question
from app.models.question_topic import QuestionTopic
from app.models.exam import Topic


async def predict_topics(
    db: AsyncSession,
    exam_id,
    subject_id,
    target_year: int,
    top_k: int = 10,
):
    """
    Returns top-K predicted topics with probabilities
    """

    stmt = (
        select(
            Topic.id,
            Topic.name,
            Question.year,
            func.count(Question.id).label("q_count"),
        )
        .join(QuestionTopic, QuestionTopic.topic_id == Topic.id)
        .join(Question, Question.id == QuestionTopic.question_id)
        .where(
            Question.exam_id == exam_id,
            Question.subject_id == subject_id,
        )
        .group_by(Topic.id, Topic.name, Question.year)
    )

    result = await db.execute(stmt)
    rows = result.all()

    year_min = min(r.year for r in rows)
    topic_scores = defaultdict(float)

    for r in rows:
        year_weight = r.year - year_min + 1
        topic_scores[r.name] += r.q_count * year_weight

    total_score = sum(topic_scores.values())

    predictions = [
        {
            "topic": topic,
            "score": round(score, 2),
            "probability": round(score / total_score, 3),
        }
        for topic, score in topic_scores.items()
    ]

    predictions.sort(key=lambda x: x["score"], reverse=True)

    return predictions[:top_k]
