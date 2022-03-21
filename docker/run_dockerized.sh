#!/usr/bin/env bash

docker run -it -v "$(pwd)"/$2:/usr/src/files/$2 \
-v "$(pwd)"/volumes/configuracion-principal.json:/usr/src/files/generators/configuracion.json \
-v "$(pwd)"/volumes/configuracion-repository-binder.json:/usr/src/files/plugins/repository-binder/configuracion.json \
-v "$(pwd)"/volumes/configuracion-variables.json:/usr/src/files/plugins/variables/configuracion.json \
-v /usr/src/files/plugins/base \
-v "$(pwd)"/volumes/descargas:/usr/src/descargas \
alexiscaspell/horrocrux "$@"