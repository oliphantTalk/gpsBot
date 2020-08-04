FROM python:3.6-alpine
COPY app /app
WORKDIR /app
#ENV FLASK_APP app.py
#ENV FLASK_RUN_HOST 0.0.0.0
#COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
