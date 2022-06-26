FROM python:3
WORKDIR /app
COPY requirements.txt requirements.txt
COPY conftest.py conftest.py
COPY secret_token.txt secret_token.txt
RUN pip3 install -r requirements.txt
RUN mkdir mini_crossword_bot
COPY mini_crossword_bot /app/mini_crossword_bot
RUN mkdir test
COPY test test/
CMD ["pytest", "test", "-W ignore::DeprecationWarning"]