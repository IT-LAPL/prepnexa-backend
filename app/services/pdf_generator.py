import io
import logging
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)


def generate_question_paper_pdf(text: str) -> io.BytesIO:
    """
    Generates PDF in-memory and returns BytesIO
    """
    logger.info("📝 Generating PDF for predicted question paper")
    # safety: cap input size to avoid enormous PDFs
    MAX_CHARS = 200_000
    if text and len(text) > MAX_CHARS:
        logger.warning(
            "Input text too long for PDF generation; truncating to %d chars", MAX_CHARS
        )
        text = text[:MAX_CHARS]

    buffer = io.BytesIO()

    try:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        story = []

        for paragraph in text.split("\n\n"):
            line = paragraph.strip()
            if not line:
                continue
            # break long paragraphs into lines for ReportLab Paragraph
            story.append(Paragraph(line.replace("\n", " "), styles["Normal"]))
            story.append(Spacer(1, 8))

        doc.build(story)

        buffer.seek(0)
        logger.info("✅ PDF generation complete")
        return buffer

    except Exception:
        logger.exception("PDF generation failed")
        # ensure buffer is reset to not return partial content
        buffer.close()
        raise
