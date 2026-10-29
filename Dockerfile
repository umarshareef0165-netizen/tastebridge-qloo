FROM python:3.12-slim
WORKDIR /app
COPY . /app
# Stdlib only: no pip install needed.
EXPOSE 7860
# Hugging Face Spaces sets PORT=7860; the server honours $PORT.
CMD ["python3", "src/server.py"]
