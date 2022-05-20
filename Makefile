docker:
	docker build -t crossword-discord .

run:
	docker run -v  $(shell pwd)/scores.db:/app/scores.db crossword-discord

.PHONY: run 