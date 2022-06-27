FROM python:3
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir mini_crossword_bot
COPY mini_crossword_bot /app/mini_crossword_bot
COPY secret_token.txt secret_token.txt
CMD ["python3", "mini_crossword_bot/bot.py"]