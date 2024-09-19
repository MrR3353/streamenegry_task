from typing import List

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select, insert, update, delete
from .database import database, metadata
from .models import notes, tags, note_tags
from .schemas import NoteCreate, NoteUpdate, NoteInDB

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Создание новой заметки
@app.post("/notes/", response_model=NoteInDB)
async def create_note(note: NoteCreate):
    # Вставка заметки
    query = notes.insert().values(title=note.title, content=note.content)
    note_id = await database.execute(query)

    # Добавление тегов
    if note.tags:
        for tag in note.tags:
            tag_id = await get_or_create_tag(tag)
            await database.execute(note_tags.insert().values(note_id=note_id, tag_id=tag_id))

    return await get_note_by_id(note_id)


# Получение всех заметок
@app.get("/notes/", response_model=List[NoteInDB])
async def get_notes():
    query = select(notes)
    rows = await database.fetch_all(query)
    notes_with_tags = [await enrich_note_with_tags(row) for row in rows]
    return notes_with_tags


# Получение заметки по ID
@app.get("/notes/{note_id}", response_model=NoteInDB)
async def get_note_by_id(note_id: int):
    query = select(notes).where(notes.c.id == note_id)
    note = await database.fetch_one(query)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return await enrich_note_with_tags(note)


# Обновление заметки
@app.put("/notes/{note_id}", response_model=NoteInDB)
async def update_note(note_id: int, note_data: NoteUpdate):
    # Проверка наличия заметки
    query = select(notes).where(notes.c.id == note_id)
    existing_note = await database.fetch_one(query)
    if existing_note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    # Обновление заметки
    update_query = notes.update().where(notes.c.id == note_id).values(
        title=note_data.title or existing_note.title,
        content=note_data.content or existing_note.content
    )
    await database.execute(update_query)

    # Обновление тегов (удаление старых, добавление новых)
    if note_data.tags is not None:
        await database.execute(delete(note_tags).where(note_tags.c.note_id == note_id))
        for tag in note_data.tags:
            tag_id = await get_or_create_tag(tag)
            await database.execute(note_tags.insert().values(note_id=note_id, tag_id=tag_id))

    return await get_note_by_id(note_id)


# Удаление заметки
@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int):
    delete_query = delete(notes).where(notes.c.id == note_id)
    result = await database.execute(delete_query)
    if result == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    await database.execute(delete(note_tags).where(note_tags.c.note_id == note_id))
    return None


# Получение или создание тега
async def get_or_create_tag(tag_name: str):
    query = select(tags.c.id).where(tags.c.name == tag_name)
    tag_id = await database.fetch_one(query)
    if tag_id:
        return tag_id[0]
    insert_query = insert(tags).values(name=tag_name)
    return await database.execute(insert_query)


# Обогащение заметки тегами
async def enrich_note_with_tags(note):
    query = select(tags.c.name).select_from(note_tags.join(tags)).where(note_tags.c.note_id == note.id)
    tag_rows = await database.fetch_all(query)
    tags_list = [tag.name for tag in tag_rows]
    return {**note, "tags": tags_list}
