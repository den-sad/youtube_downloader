FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN apt update -y
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
WORKDIR /app
COPY ./app /app
CMD [ "python3", "app.py" ]