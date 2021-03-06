# Horrocrux
![alt text](img/logo.jpg)

> Inmortaliza tu trabajo o codigo hasta el final de los tiempos
---

## Indice

* [Para empezar](#para-empezar)
* [Prerrequisitos](#prerrequisitos)
* [Despliegue](#despliegue)
* [Parametros](#parametros)
* [Configuracion](#configuracion)
* [Plugins](plugins.md)
* [Autor](#autor)

---


## Para empezar

Clonar el proyecto de git o descargar en archivo .zip/.tar.gz y descomprimir


## Prerrequisitos

- python 3.8 o superior


## Uso

En primera instancia es necesario tener las dependencias instaladas, estas se instalan de la sig. manera:
```
pip install -r requirements.txt
```

Tambien se puede correr con docker con el siguiente comando: 
```
cd docker
chmod +x run_dockerized.sh
./run_dockerized.sh
```

Para levantar el proyecto solo es necesario ejecutar:
```
python project_generator.py unNombreDeProyecto unPath
```

### Se mostrara una interfaz como la siguiente: 
![alt text](img/interfaz1.png)

- En el campo nombre se especifica el nombre del proyecto, luego en el listbox de plugins se deberia poder agregar plugins seleccionando cada uno y pulsando en el boton Add.
- Para configurar los plugins se tiene otro listbox de plugins seleccionados en el cual se puede seleccionar uno por uno cada plugin y borrarlo con el boton Delete o editarlo con el boton Edit
- Si se quiere salir pulsar el boton Quit

Luego de configurar todo se aprieta el boton Build y se deberia obtener algo parecido a esto:
![alt text](img/interfaz2.png)

Finalmente dentro de la carpeta docker se tendra una carpeta con el proyecto creado

## Parametros

- Como primer parametro se le pasa el nombre del proyecto (obligatorio).
- Como segundo parametro se le pasa el path donde sera creado el proyecto (opcional).

## Configuracion

En ./generators/configuracion.json se puede configurar las opciones principales del generador, para configurar los plugins hacerlo desde ./plugins/nombreDelPlugin/[configuracion.json](plugins.md).

- **path_plugin_principal**: Es el path en el cual se encuentra el plugin base, osea el template que se usara como proyecto principal.
- **ejecutar_plugin_principal_al_inicio**: Indica si se debe ejecutar el plugin principal antes que los demas plugins o despues.
- **plugins**: Es una lista con los nombres de todos los plugins de los cuales se podra disponer (no hace falta poner el base), los nombres de estos deben de respetar los nombres de las carpetas en la carpeta ***plugins***.
- **variables**: Lista de nombres de variables que se podran usar en cualquier plugin a traves de ***@@nombreDeVariable*** (por default estan nombre_proyecto y path_proyecto), estas variables se deben disponibilizar en el index de un plugin de la siguiente manera:

    ```
    yeoman_handler.configuracion.agregar_variable("nombreDeVariable");
    ```

## Autor

> **Alexis Taberna**

* DockerHub: [alexistaberna](https://hub.docker.com/u/alexiscaspell)
