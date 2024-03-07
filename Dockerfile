FROM python:3.10.11
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y libpq-dev gcc python3-dev python3-pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . ./popug_area
WORKDIR /popug_area
