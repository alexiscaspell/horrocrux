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
ADD ./src ./app/src
COPY ./project_generator.py ./app/project_generator.py
ADD ./files ./files
RUN mkdir descargas

RUN find ./app -type f -exec sed -i -e "s#import horrocrux.#import src.horrocrux.#g" -e "s#from horrocrux.#from src.horrocrux.#g" {} \;

RUN python -m compile -b -f -o ./dist ./app
RUN mv -f ./dist/app/* .

RUN rm -r ./app