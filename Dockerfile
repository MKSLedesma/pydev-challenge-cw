FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY tests/ ./tests/
COPY main.py ./

CMD ["sh", "-c", "python -m pytest tests -v && python main.py"]