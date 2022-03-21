FROM python:3.8

# CONFIGURACION
ARG TAG=latest

WORKDIR /usr/src

COPY ./scripts/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh","asd"]

# DEPENDENCIAS
RUN pip install compile --upgrade pip

COPY ./requirements.txt .

RUN pip install -r requirements.txt
RUN rm requirements.txt

# COMPILACION
ADD ./apps ./src/apps
COPY ./project_generator.py ./src/project_generator.py
ADD ./files ./files
RUN mkdir descargas

RUN python -m compile -b -f -o ./dist ./src
RUN mv -f ./dist/src/* .

RUN rm -r ./src
