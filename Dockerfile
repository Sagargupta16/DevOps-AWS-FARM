FROM python:3.11-alpine
WORKDIR /app
COPY . /app/
RUN apk add --no-cache gcc musl-dev python3-dev && \
    pip install --upgrade pip && \
    pip install cython && \
    pip install -r requirements.txt && \
    pip install pyyaml==6.0.1
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]