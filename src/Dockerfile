FROM python:3
# RUN curl -sL https://deb.nodesource.com/setup_13.x | sudo -E bash -
# RUN sudo apt-get install -y nodejs
RUN mkdir /code
WORKDIR /code
RUN pip install pipenv
COPY Pipfile /code/
COPY Pipfile.lock /code/
RUN pipenv install --system
COPY . /code/
