docker:
	docker build -t crossword-discord .

run:
	docker run -v  $(shell pwd)/scores.db:/app/scores.db crossword-discord

clean:
	find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$|\.pytest_cache)" | xargs rm -rf

test:
	docker build -f Test.Dockerfile -t crossword-test .
	docker run crossword-test 

.PHONY: run clean test