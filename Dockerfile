FROM python:3
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY mini_crossword_bot.py mini_crossword_bot.py
COPY secret_token.txt secret_token.txt
CMD ["python3", "mini_crossword_bot.py"]