import random

from app.database import DB_CONFIG, DatabaseUnavailableError, get_database_connection, initialize_dictionary_database


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