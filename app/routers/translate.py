from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

from app.database import DatabaseUnavailableError, initialize_dictionary_database
from app.html_pages import render_translate_page
from app.translation import TranslationResponse, setup_ai_client


router = APIRouter()
ai_client = setup_ai_client()


@router.get("/translate", response_class=HTMLResponse)
def translate_form(status_message: str = ""):
    try:
        initialize_dictionary_database()
        return render_translate_page(status_message=status_message)
    except DatabaseUnavailableError as exc:
        return render_translate_page(status_message=str(exc))


@router.post("/translate", response_class=HTMLResponse)
def translate_text(text: str = Form(...)):
    try:
        initialize_dictionary_database()
    except DatabaseUnavailableError as exc:
        return render_translate_page(text=text, status_message=str(exc))

    if ai_client is None:
        return render_translate_page(
            text=text,
            status_message="Missing HF_TOKEN environment variable. Set it to enable AI translation.",
        )

    completion = ai_client.chat.completions.create(
        model="moonshotai/Kimi-K2-Instruct-0905",
        messages=[
            {
                "role": "user",
                "content": f"Return two sentences. First should be a normal translation from German to English of the word {text}, with variants or explanations where necessary. The second should only be one word(or phrase where necessary)- the most likely translation, as few-worded as possible.",
            }
        ],
    )

    response_text = completion.choices[0].message.content or ""
    response_lines = [line.strip() for line in response_text.splitlines() if line.strip()]
    translation = TranslationResponse(
        detailed_translation=response_lines[0] if len(response_lines) > 0 else "",
        concise_translation=response_lines[1] if len(response_lines) > 1 else "",
    )

    return render_translate_page(
        text=text,
        translated_text=translation.detailed_translation,
        concise_translation=translation.concise_translation,
    )