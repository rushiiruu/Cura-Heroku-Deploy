FROM python:3.9-slim-buster

# Install Tesseract and its dependencies
RUN apt-get update && \
    apt-get -qq -y install tesseract-ocr && \
    apt-get -qq -y install libtesseract-dev && \
    apt-get -qq -y install tesseract-ocr-eng

# Verify Tesseract installation
RUN tesseract --version

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "app.py"]

