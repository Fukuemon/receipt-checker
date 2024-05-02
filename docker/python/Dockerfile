FROM python:3.10-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY ../../server/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app/api
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]