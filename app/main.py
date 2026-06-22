from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn
from openai import OpenAI
import os
import json
import random
import importlib
from pydantic import BaseModel
from html import escape

app = FastAPI()
hf_token = os.getenv("HF_TOKEN")
ai_client = (
    OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=hf_token,
    )
    if hf_token
    else None
)

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
    "database": os.getenv("MYSQL_DATABASE", "language_learner"),
}

SEED_DICTIONARY_ENTRIES = [
    ("Haus", "house"),
    ("Wasser", "water"),
    ("Buch", "book"),
    ("Katze", "cat"),
    ("Brot", "bread"),
    ("Danke", "thank you"),
    ("Bitte", "please"),
    ("Freund", "friend"),
    ("Straße", "street"),
    ("Schule", "school"),
    ("Sonne", "sun"),
    ("Apfel", "apple"),
    ("Liebe", "love"),
    ("Zeit", "time"),
    ("Morgen", "morning"),
]


class TranslationResponse(BaseModel):
    detailed_translation: str
    concise_translation: str


class DatabaseUnavailableError(RuntimeError):
    pass


def get_database_connection():
    mysql_connector = importlib.import_module("mysql.connector")
    return mysql_connector.connect(**DB_CONFIG)


def ensure_dictionary_database_exists():
    mysql_connector = importlib.import_module("mysql.connector")
    try:
        connection = mysql_connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
    except Exception as exc:
        raise DatabaseUnavailableError(
            f"MySQL is unavailable at {DB_CONFIG['host']}:{DB_CONFIG['port']}. "
            "Check the database container, host, and port settings."
        ) from exc
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


def initialize_dictionary_database():
    ensure_dictionary_database_exists()
    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS dictionary_entries (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        german_word VARCHAR(255) NOT NULL,
                        english_translation VARCHAR(255) NOT NULL
                    )
                    """
                )
                cursor.execute("SELECT COUNT(*) FROM dictionary_entries")
                existing_count = cursor.fetchone()[0]
                if existing_count == 0:
                    seed_entries = random.sample(SEED_DICTIONARY_ENTRIES, 10)
                    cursor.executemany(
                        "INSERT INTO dictionary_entries (german_word, english_translation) VALUES (%s, %s)",
                        seed_entries,
                    )
            connection.commit()
    except DatabaseUnavailableError:
        raise
    except Exception as exc:
        raise DatabaseUnavailableError(
            f"MySQL is unavailable at {DB_CONFIG['host']}:{DB_CONFIG['port']}. "
            "Check the database container, host, and port settings."
        ) from exc


def get_learn_practice_data(exclude_german_word: str = ""):
    initialize_dictionary_database()
    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT german_word, english_translation FROM dictionary_entries")
                entries = cursor.fetchall()
    except DatabaseUnavailableError:
        raise
    except Exception as exc:
        raise DatabaseUnavailableError(
            f"MySQL is unavailable at {DB_CONFIG['host']}:{DB_CONFIG['port']}. "
            "Check the database container, host, and port settings."
        ) from exc

    if exclude_german_word:
        filtered_entries = [entry for entry in entries if entry[0] != exclude_german_word]
        if filtered_entries:
            entries = filtered_entries

    if not entries:
        return "", [], ""

    target_entry = random.choice(entries)
    target_translation = target_entry[1]

    candidate_options = []
    seen_options = {target_translation}
    for entry in entries:
        translation = entry[1]
        if translation not in seen_options:
            candidate_options.append(translation)
            seen_options.add(translation)

    random.shuffle(candidate_options)
    options = candidate_options[:5]
    options.append(target_translation)
    random.shuffle(options)

    return target_entry[0], options, target_translation


def render_translate_page(text: str = "", translated_text: str = "", concise_translation: str = "", status_message: str = ""):
    page = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Translate</title>
                <style>
                    :root {
                        color-scheme: light;
                        font-family: Arial, sans-serif;
                        background: #f4f7fb;
                        color: #1f2937;
                    }

                    body {
                        margin: 0;
                        min-height: 100vh;
                        display: grid;
                        place-items: center;
                        padding: 24px;
                        background: linear-gradient(135deg, #eef4ff, #f8fafc 60%, #fff7ed);
                    }

                    .card {
                        width: min(100%, 560px);
                        background: white;
                        border: 1px solid #dbe4f0;
                        border-radius: 20px;
                        padding: 28px;
                        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
                    }

                    h1 {
                        margin: 0 0 8px;
                        font-size: 2rem;
                    }

                    .top-nav {
                        display: flex;
                        gap: 10px;
                        margin-bottom: 16px;
                    }

                    .top-nav a {
                        flex: 1;
                        text-align: center;
                        text-decoration: none;
                        border: 1px solid #c9d5e3;
                        border-radius: 999px;
                        padding: 10px 12px;
                        font-weight: 700;
                        color: #334155;
                        background: #f8fafc;
                    }

                    .top-nav a.active {
                        background: #0f172a;
                        border-color: #0f172a;
                        color: #ffffff;
                    }

                    p {
                        margin: 0 0 20px;
                        color: #5b6472;
                    }

                    label {
                        display: block;
                        font-weight: 600;
                        margin-bottom: 8px;
                    }

                    textarea {
                        width: 100%;
                        min-height: 140px;
                        resize: vertical;
                        border: 1px solid #c9d5e3;
                        border-radius: 14px;
                        padding: 14px;
                        font: inherit;
                        box-sizing: border-box;
                    }

                    input {
                        width: 100%;
                        border: 1px solid #c9d5e3;
                        border-radius: 14px;
                        padding: 12px 14px;
                        font: inherit;
                        box-sizing: border-box;
                        margin-bottom: 10px;
                    }

                    .inline-fields {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 12px;
                        margin-top: 4px;
                    }

                    .inline-fields > div {
                        min-width: 0;
                    }

                    button {
                        margin-top: 14px;
                        border: 0;
                        border-radius: 999px;
                        padding: 12px 18px;
                        background: #0f172a;
                        color: white;
                        font: inherit;
                        font-weight: 700;
                        cursor: pointer;
                    }

                    .secondary {
                        margin-top: 10px;
                        background: #334155;
                    }

                    .hint {
                        margin-top: 12px;
                        font-size: 0.95rem;
                        color: #64748b;
                    }

                    .status {
                        margin-top: 14px;
                        padding: 10px 14px;
                        border-radius: 12px;
                        background: #ecfeff;
                        color: #155e75;
                        font-weight: 700;
                    }
                </style>
            </head>
            <body>
                <main class="card">
                    <header class="top-nav" aria-label="Main sections">
                        <a href="/translate" class="active">Translate</a>
                        <a href="/learn">Learn</a>
                    </header>
                    <h1>Translate from German to English</h1>
                    <p>Type a word below and submit it to your backend.</p>
                    <form method="post" action="/translate">
                        <label for="text">Word to translate</label>
                        <textarea id="text" name="text" placeholder="Enter word here...">__TEXT__</textarea>
                        <button type="submit">Translate</button>

                        <label for="translated_text">Explained translation</label>
                        <textarea id="translated_text" name="translated_text" placeholder="Translated result will appear here..." readonly>__TRANSLATED_TEXT__</textarea>
                        
                        <div class="inline-fields">
                            <div>
                                <label for="dictionary_word">Word/Phrase</label>
                                <input id="dictionary_word" name="dictionary_word" placeholder="e.g. hello" value="__TEXT__"  />
                            </div>
                            <div>
                                <label for="dictionary_meaning">Meaning/Translation</label>
                                <input id="dictionary_meaning" name="dictionary_meaning" placeholder="e.g. hola" value="__CONCISE_TRANSLATION__"  />
                            </div>
                        </div>

                        <button type="submit" class="secondary" formaction="/dictionary/add" formmethod="post">Add to dictionary</button>
                    </form>
                    __STATUS_MESSAGE__
                </main>
            </body>
        </html>
        """
    return (
        page.replace("__TEXT__", escape(text))
        .replace("__TRANSLATED_TEXT__", escape(translated_text))
        .replace("__CONCISE_TRANSLATION__", escape(concise_translation))
        .replace(
            "__STATUS_MESSAGE__",
            f'<div class="status">{escape(status_message)}</div>' if status_message else "",
        )
    )


def render_learn_page(german_word: str, options: list[str], correct_answer: str, feedback_message: str = ""):
    option_buttons = "\n".join(
        f'<button type="submit" name="selected_answer" value="{escape(option)}">{escape(option)}</button>'
        for option in options
    )
    feedback_block = f'<div class="status">{escape(feedback_message)}</div>' if feedback_message else ""
    return f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Learn</title>
                <style>
                    :root {{
                        color-scheme: light;
                        font-family: Arial, sans-serif;
                        background: #f4f7fb;
                        color: #1f2937;
                    }}

                    body {{
                        margin: 0;
                        min-height: 100vh;
                        display: grid;
                        place-items: center;
                        padding: 24px;
                        background: linear-gradient(135deg, #eef4ff, #f8fafc 60%, #fff7ed);
                    }}

                    .card {{
                        width: min(100%, 560px);
                        background: white;
                        border: 1px solid #dbe4f0;
                        border-radius: 20px;
                        padding: 28px;
                        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
                    }}

                    h1 {{
                        margin: 0 0 8px;
                        font-size: 2rem;
                    }}

                    .top-nav {{
                        display: flex;
                        gap: 10px;
                        margin-bottom: 16px;
                    }}

                    .top-nav a {{
                        flex: 1;
                        text-align: center;
                        text-decoration: none;
                        border: 1px solid #c9d5e3;
                        border-radius: 999px;
                        padding: 10px 12px;
                        font-weight: 700;
                        color: #334155;
                        background: #f8fafc;
                    }}

                    .top-nav a.active {{
                        background: #0f172a;
                        border-color: #0f172a;
                        color: #ffffff;
                    }}

                    p {{
                        margin: 0 0 16px;
                        color: #5b6472;
                    }}

                    label {{
                        display: block;
                        font-weight: 600;
                        margin-bottom: 8px;
                    }}

                    input {{
                        width: 100%;
                        border: 1px solid #c9d5e3;
                        border-radius: 14px;
                        padding: 12px 14px;
                        font: inherit;
                        box-sizing: border-box;
                        margin-bottom: 14px;
                        background: #f8fafc;
                        color: #0f172a;
                    }}

                    .chip-grid {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px;
                    }}

                    .chip-grid button {{
                        border: 1px solid #c9d5e3;
                        background: #f8fafc;
                        color: #334155;
                        border-radius: 999px;
                        padding: 10px 14px;
                        font: inherit;
                        font-weight: 700;
                        cursor: pointer;
                    }}

                    .status {{
                        margin-top: 14px;
                        padding: 10px 14px;
                        border-radius: 12px;
                        background: #ecfeff;
                        color: #155e75;
                        font-weight: 700;
                    }}
                </style>
            </head>
            <body>
                <main class="card">
                    <header class="top-nav" aria-label="Main sections">
                        <a href="/translate">Translate</a>
                        <a href="/learn" class="active">Learn</a>
                    </header>
                    <h1>Learn</h1>
                    <p>Select the correct English translation for the German word below.</p>
                    <form method="post" action="/learn/answer">
                        <label for="learn_text">German word</label>
                        <input id="learn_text" name="learn_text" value="{escape(german_word)}" disabled />
                        <input type="hidden" name="german_word" value="{escape(german_word)}" />
                        <input type="hidden" name="correct_answer" value="{escape(correct_answer)}" />
                        <input type="hidden" name="options_json" value="{escape(json.dumps(options))}" />

                        <div class="chip-grid" aria-label="Practice phrases">
                            {option_buttons}
                        </div>
                    </form>
                    {feedback_block}
                </main>
            </body>
        </html>
    """


@app.get("/translate", response_class=HTMLResponse)
def translate_form():
    try:
        initialize_dictionary_database()
        return render_translate_page()
    except DatabaseUnavailableError as exc:
        return render_translate_page(status_message=str(exc))


@app.get("/learn", response_class=HTMLResponse)
def learn_page():
        try:
            german_word, options, correct_answer = get_learn_practice_data()
            return render_learn_page(german_word, options, correct_answer)
        except DatabaseUnavailableError as exc:
            return render_learn_page("", [], "", str(exc))


@app.post("/learn/answer", response_class=HTMLResponse)
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
        else:
            return render_learn_page(
                german_word,
                options,
                correct_answer,
                "This one was incorrect.",
            )


@app.post("/dictionary/add", response_class=HTMLResponse)
def add_dictionary_entry(dictionary_word: str = Form(...), dictionary_meaning: str = Form(...), text: str = Form("")):
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
            return render_translate_page(
                text=text or dictionary_word,
                translated_text=dictionary_meaning,
                concise_translation=dictionary_meaning,
                status_message=str(exc),
            )

        return render_translate_page(
            text=text or dictionary_word,
            translated_text=dictionary_meaning,
            concise_translation=dictionary_meaning,
            status_message="Added to dictionary.",
        )


@app.post("/translate", response_class=HTMLResponse)
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
                "content": f"Return two sentences. First should be a normal translation from German to English of the word {text}, with variants or explanations where necessary. The second should only be one word(or phrase where necessary)- the most likely translation, as few-worded as possible."
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)