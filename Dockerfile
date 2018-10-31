FROM python:3.6.4

ADD /drchrono /app
ADD requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

CMD /app/scripts/entrypoint.sh
