# IMPORTANT: import order does not matter, only that all are imported

from app.models.user import User
from app.models.upload import Upload
from app.models.file import File
from app.models.processed_text import ProcessedText
from app.models.exam import Exam, Subject, Topic
from app.models.question import Question
from app.models.question_topic import QuestionTopic
