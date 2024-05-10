FROM python:3.10-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /server
COPY ../../server/requirements.txt /server/requirements.txt
RUN pip install -r requirements.txt

WORKDIR /server/api
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]