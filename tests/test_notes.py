import pytest
from httpx import AsyncClient
from notes.main import app
from notes.database import database  # Проверьте импорт вашей базы данных


# Фикстура для настройки подключения и отключения базы данных
@pytest.fixture(autouse=True)
async def setup_and_teardown():
    # Подключение к базе данных перед тестами
    await database.connect()
    print("Подключение к базе данных выполнено.")

    # yield - разделяет код перед тестом и после теста
    yield

    # Отключение от базы данных после тестов
    await database.disconnect()
    print("Отключение от базы данных выполнено.")


# Тест создания новой заметки
@pytest.mark.asyncio
async def test_create_note():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.post("/notes/",
                                 json={"title": "New Note", "content": "New content", "tags": ["fastapi", "test"]})

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["title"] == "New Note"
    assert json_data["content"] == "New content"
    assert set(json_data["tags"]) == {"fastapi", "test"}

# import pytest
# from httpx import AsyncClient
# from sqlalchemy import insert, delete
# from notes.main import app
# from notes.database import database
# from notes.models import notes, tags, note_tags
#
#
# @pytest.fixture(autouse=True)
# async def setup_and_teardown():
#     # Код, выполняющийся перед тестом (подключение к базе данных)
#     await database.connect()
#     print("Подключение к базе данных выполнено.")
#     # yield - разделяет код "до" и "после"
#     yield
#     # Код, выполняющийся после теста (отключение от базы данных)
#     # await database.disconnect()
#     print("Отключение от базы данных выполнено.")
#
#
# @pytest.mark.asyncio
# async def test_create_note():
#     async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
#         response = await ac.post("/notes/",
#                                  json={"title": "New Note", "content": "New content", "tags": ["fastapi", "test"]})
#
#     assert response.status_code == 200
#     json_data = response.json()
#     assert json_data["title"] == "New Note"
#     assert json_data["content"] == "New content"
#     assert set(json_data["tags"]) == {"fastapi", "test"}


# @pytest.fixture
# async def setup_test_data():
#     # Предварительная очистка данных
#     await database.execute(delete(note_tags))
#     await database.execute(delete(tags))
#     await database.execute(delete(notes))
#
#     # Создание тестовой заметки
#     query = insert(notes).values(title="Test Note", content="This is a test note")
#     note_id = await database.execute(query)
#
#     yield note_id  # Тесты будут работать с этим ID
#
#     # Очистка после тестов
#     await database.execute(delete(note_tags))
#     await database.execute(delete(tags))
#     await database.execute(delete(notes))
#


# @pytest.mark.asyncio
# async def test_get_notes(setup_test_data):
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get("/notes/")
#
#     assert response.status_code == 200
#     json_data = response.json()
#     assert len(json_data) > 0
#     assert json_data[0]["title"] == "Test Note"
#     assert json_data[0]["content"] == "This is a test note"
#
#
# @pytest.mark.asyncio
# async def test_get_note_by_id(setup_test_data):
#     note_id = setup_test_data
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get(f"/notes/{note_id}")
#
#     assert response.status_code == 200
#     json_data = response.json()
#     assert json_data["id"] == note_id
#     assert json_data["title"] == "Test Note"
#     assert json_data["content"] == "This is a test note"
#
#
# @pytest.mark.asyncio
# async def test_update_note():
#     # Создаем заметку для обновления
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/notes/",
#                                  json={"title": "Note to Update", "content": "Initial content", "tags": ["initial"]})
#     note_id = response.json()["id"]
#
#     # Обновляем заметку
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         update_response = await ac.put(f"/notes/{note_id}", json={"title": "Updated Note", "content": "Updated content",
#                                                                   "tags": ["updated"]})
#
#     assert update_response.status_code == 200
#     json_data = update_response.json()
#     assert json_data["title"] == "Updated Note"
#     assert json_data["content"] == "Updated content"
#     assert set(json_data["tags"]) == {"updated"}
#
#
# @pytest.mark.asyncio
# async def test_delete_note():
#     # Создаем заметку для удаления
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/notes/",
#                                  json={"title": "Note to Delete", "content": "Will be deleted", "tags": ["delete"]})
#     note_id = response.json()["id"]
#
#     # Удаляем заметку
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         delete_response = await ac.delete(f"/notes/{note_id}")
#
#     assert delete_response.status_code == 204
#
#     # Проверяем, что заметка действительно удалена
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         get_response = await ac.get(f"/notes/{note_id}")
#
#     assert get_response.status_code == 404
