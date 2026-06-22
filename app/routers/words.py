from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from urllib.parse import quote_plus

from app.database import DatabaseUnavailableError, get_database_connection, initialize_dictionary_database
from app.html_pages import render_translate_page
from pydantic import BaseModel


router = APIRouter()


class WordTranslationResponse(BaseModel):
    word: str
    translation: str


def _extract_word_payload(payload: dict) -> tuple[str, str]:
    dictionary_word = (payload.get("word") or payload.get("dictionary_word") or "").strip()
    dictionary_meaning = (payload.get("translation") or payload.get("dictionary_meaning") or "").strip()

    if not dictionary_word or not dictionary_meaning:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Both 'word' and 'translation' are required.",
        )

    return dictionary_word, dictionary_meaning


@router.post("/words", status_code=status.HTTP_201_CREATED)
async def add_dictionary_entry(request: Request):
    content_type = (request.headers.get("content-type") or "").lower()

    if "application/json" in content_type:
        payload = await request.json()
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form_data = await request.form()
        payload = dict(form_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Send JSON or form data.",
        )

    try:
        dictionary_word, dictionary_meaning = _extract_word_payload(payload)
    except HTTPException as exc:
        if "text/html" in (request.headers.get("accept") or "").lower():
            return RedirectResponse(url="/translate?status_message=" + quote_plus(exc.detail), status_code=status.HTTP_303_SEE_OTHER)
        raise exc
    try:
        initialize_dictionary_database()
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO dictionary_entries (german_word, english_translation) VALUES (%s, %s)",
                    (dictionary_word.strip(), dictionary_meaning.strip()),
                )
            connection.commit()
    except DatabaseUnavailableError as exc:
        if "text/html" in (request.headers.get("accept") or "").lower():
            return RedirectResponse(url="/translate?status_message=" + quote_plus(str(exc)), status_code=status.HTTP_303_SEE_OTHER)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    if "text/html" in (request.headers.get("accept") or "").lower() or "form-data" in content_type:
        return RedirectResponse(url="/translate?status_message=" + quote_plus("Added to dictionary."), status_code=status.HTTP_303_SEE_OTHER)

    return WordTranslationResponse(word=dictionary_word, translation=dictionary_meaning)

class WordTranslationResponse(BaseModel):
    word: str
    translation: str


@router.get("/words", response_model=list[WordTranslationResponse])
def list_dictionary_entries():
    try:
        initialize_dictionary_database()
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT german_word, english_translation FROM dictionary_entries ORDER BY id DESC"
                )
                rows = cursor.fetchall()
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return [
        WordTranslationResponse(word=row[0], translation=row[1])
        for row in rows
    ]


@router.get("/words/{word}", response_model=WordTranslationResponse)
def retrieve_dictionary_entry(word: str):
    try:
        initialize_dictionary_database()
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT english_translation FROM dictionary_entries WHERE german_word = %s ORDER BY id DESC LIMIT 1",
                    (word.strip(),),
                )
                row = cursor.fetchone()
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No translation found for "{word}".')

    return WordTranslationResponse(word=word.strip(), translation=row[0])