FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Download the required NLTK tokenizer during build
RUN python -c "import nltk; nltk.download('punkt')"

EXPOSE 5000

CMD ["python", "app.py"]
