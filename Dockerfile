FROM python:3.8
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY InMemDb.py InMemDb.py
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]

