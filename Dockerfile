FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pytest.ini ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY main.py ./

CMD ["sh", "-c", "python -m pytest -v && python main.py"]