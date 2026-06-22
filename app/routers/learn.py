import json

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.database import DatabaseUnavailableError
from app.html_pages import render_learn_page
from app.learning import get_learn_practice_data


router = APIRouter()


class LearnPracticeResponse(BaseModel):
    german_word: str
    options: list[str]
    correct_answer: str


@router.get("/learn", response_model=LearnPracticeResponse)
def learn_api():
    german_word, options, correct_answer = get_learn_practice_data()
    return LearnPracticeResponse(
        german_word=german_word,
        options=options,
        correct_answer=correct_answer,
    )


@router.get("/learn/view", response_class=HTMLResponse)
def learn_page():
    try:
        german_word, options, correct_answer = get_learn_practice_data()
        return render_learn_page(german_word, options, correct_answer)
    except DatabaseUnavailableError as exc:
        return render_learn_page("", [], "", str(exc))


@router.post("/learn/answer", response_class=HTMLResponse)
def learn_answer(
    german_word: str = Form(...),
    correct_answer: str = Form(...),
    options_json: str = Form(...),
    selected_answer: str = Form(...),
):
    options = json.loads(options_json)
    if selected_answer == correct_answer:
        new_german_word, new_options, new_correct_answer = get_learn_practice_data(german_word)
        return render_learn_page(
            new_german_word,
            new_options,
            new_correct_answer,
            "Correct.",
        )

    return render_learn_page(
        german_word,
        options,
        correct_answer,
        "This one was incorrect.",
    )