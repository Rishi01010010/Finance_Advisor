FROM python:3.10-slim

WORKDIR /app

COPY . /app
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["streamlit", "run", "streamlit_app/app.py", "--server.port=8501", "--server.enableCORS=false"]