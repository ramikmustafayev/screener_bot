import tempfile
import pandas as pd
from sqlalchemy import text
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


async def execute_query_to_pdf(message,session, query: str) -> str | None:
    """Выполняет SQL-запрос и сохраняет PDF-файл с результатами. Возвращает путь к файлу или None."""
    try:
        result = await session.execute(text(query))

        # Проверка: возвращает ли запрос строки
        if result.returns_rows:
            rows = result.fetchall()
            if not rows:
                return 'EMPTY'

            headers = result.keys()
            df = pd.DataFrame(rows, columns=headers)

            # Создание временного PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                file_path = tmp.name

            doc = SimpleDocTemplate(file_path, pagesize=letter)
            data = [df.columns.tolist()] + df.values.tolist()
            table = Table(data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            doc.build([table])
            return file_path
        else:
            await session.commit()
            # Если запрос не возвращает строки — просто подтверждаем выполнение
            return "NO_ROWS"

    except Exception as e:
        await message.answer(f"Ошибка при выполнении SQL-запроса: {e}")
        return None