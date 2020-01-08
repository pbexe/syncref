FROM python:3
RUN mkdir /code
WORKDIR /code
RUN pip install pipenv
COPY Pipfile /code/
COPY Pipfile.lock /code/
RUN pipenv install --system
COPY . /code/
RUN python manage.py collectstatic