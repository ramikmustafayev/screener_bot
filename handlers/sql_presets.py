import os
import html
from aiogram import Router
from aiogram.types import Message,FSInputFile
from aiogram.filters import Command
from services.sql_queries import execute_query_to_pdf
from database.repo.requests import RequestsRepo
from database.repo.sql_presets import SQLPresetsRepo


sql_preset_router=Router()






@sql_preset_router.message(Command("add_preset"))
async def add_preset(message: Message, repo: RequestsRepo, user):
    try:
        text = message.text.removeprefix("/add_preset").strip()
        if ":" not in text:
            await message.answer("Формат: название : SQL-запрос")
            return
        
        name, query = map(str.strip, text.split(":", 1))

        sql_repo: SQLPresetsRepo = repo.sql_presets

        await sql_repo.add(name=name, query=query, user_id=user.id)

        await message.answer(f"✅ Пресет '{name}' добавлен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении пресета: {e}")


@sql_preset_router.message(Command("delete_preset"))
async def delete_preset(message: Message, repo: RequestsRepo, user):
    try:
        id = message.text.removeprefix("/delete_preset").strip()
        if not id:
            await message.answer("Формат: /delete_preset Id пресета")
            return

    

        sql_repo: SQLPresetsRepo = repo.sql_presets

        row_count=await sql_repo.delete({'id':int(id),'user_id':user.id})


        if row_count == 0:
            await message.answer(f"❌ Пресет c Id '{id}' не найден.")
        else:
            await message.answer(f"✅ Пресет c Id '{id}' удалён.")

  
    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении пресета: {e}")



@sql_preset_router.message(Command("list_presets"))
async def list_presets(message: Message, repo:RequestsRepo,user):
    presets_repo=repo.sql_presets

    presets=await presets_repo.get_all(user_id=user.id)

    if not presets:
        await message.answer("⚠️ Пресеты отсутствуют.")
        return

    text = "📄 Список пресетов:\n\n"
    for preset in presets:
        text += f"• Id:{preset.id} name:{preset.name}\n"

    await message.answer(text)



@sql_preset_router.message(Command("run_preset"))
async def handle_sql_query(message: Message,repo:RequestsRepo,user,session):
    id = message.text.removeprefix("/run_preset").strip()
    if not id:
        await message.answer("Формат: /run_preset Id пресета")
        return
    
    presets_repo=repo.sql_presets

    preset=await presets_repo.get_one_or_none(user_id=user.id,id=int(id))

 
    pdf_path = await execute_query_to_pdf(message,session, preset.query)
    if pdf_path == "NO_ROWS":
        await message.answer("Запрос выполнен успешно. Строк для отображения нет.")
    elif pdf_path=='EMPTY':
        await message.answer("Запрос выполнен успешно, ничего не вернул")
    elif pdf_path:
        await message.answer_document(FSInputFile(pdf_path, filename="result.pdf"))
        os.remove(pdf_path)
   


@sql_preset_router.message(Command("get_preset"))
async def get_preset(message: Message,repo,user):
    # Получаем название пресета от пользователя
    id = message.text.removeprefix("/get_preset").strip()

    if not id:
        await message.answer("Формат: /run_preset Id пресета")
        return
    
    presets_repo=repo.sql_presets

    preset=await presets_repo.get_one_or_none(user_id=user.id,id=int(id))

    if preset:
        query = html.escape(preset.query) 
        # Если нашли пресет, отправляем запрос
        await message.answer(
    f"Запрос для пресета с Id '{id}':\n\n<pre>{query}</pre>",
    parse_mode='HTML'
)
    else:
        # Если не нашли, уведомляем пользователя
        await message.answer(f"Пресет с  '{id}' не найден.")
