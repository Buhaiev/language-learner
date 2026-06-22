
import json
from html import escape


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
                        <a href="/learn/view">Learn</a>
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

                        <button type="submit" class="secondary" formaction="/words" formmethod="post">Add to dictionary</button>
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
                        <a href="/learn/view" class="active">Learn</a>
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