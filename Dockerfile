FROM python:3.7.6-slim-buster

ENV PATH "/root/.poetry/bin:${PATH}"

RUN apt-get update && apt-get upgrade -y && \
	apt-get install git curl gcc python3-pyqt5 pyqt5-dev-tools qttools5-dev-tools -y && \
	pip install --upgrade pip && \
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python && \
	poetry --version && \
	git clone https://github.com/fferegrino/voltorb-flip-ui.git

WORKDIR /voltorb-flip-ui

RUN poetry run pip install --upgrade pip && poetry install
