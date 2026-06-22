FROM python:3.13.3-alpine
WORKDIR /app
COPY requirements.txt ./
COPY app ./app
RUN pip install -r requirements.txt
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"]