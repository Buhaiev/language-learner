# Language Learner

Language Learner is a small web application for learning foreign vocabulary.
Users can translate new words, save them to a personal vocabulary list, and test themselves with simple multiple-choice exercises.

The project was built as a practical backend learning project using **FastAPI**, **Pydantic**, **MySQL**, and **Docker**.

## Features

* Translate foreign words using an external AI/translation provider
* Save translated words to a MySQL-backed vocabulary list
* Add vocabulary entries manually
* Practise saved words through a simple learning/revision page
* Check whether a selected answer is correct
* Expose REST-style endpoints for vocabulary operations
* Run the application and database with Docker Compose

## Tech Stack

* **Python**
* **FastAPI**
* **Pydantic**
* **MySQL**
* **Docker**
* **Docker Compose**
* **Hugging Face API** for translation support



## Environment Variables

Create a `.env` file in the project root before running the application. `.env-example` is included into the repository to show which variables are needed. 

## Running the Project with Docker Compose

From the project root, run:

```bash
docker compose -f compose.yml up --build
```

The application should then be available at:

```text
http://localhost:8001
```

FastAPI documentation is available at:

```text
http://localhost:8001/docs
```

## License

This project is licensed under the GPL-3.0 License.
