FROM python:3
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN python3 db_setup_script.py
CMD ["python3", "mini_crossword_bot.py"]