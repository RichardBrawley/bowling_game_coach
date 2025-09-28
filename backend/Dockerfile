FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PORT=8000
EXPOSE 8000

# If deploying with an API key:
# ENV OPENAI_API_KEY=<your key>
# ENV OPENAI_MODEL=gpt-4o-mini

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
