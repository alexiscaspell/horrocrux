from apps.models.plugin import Plugin, Copia, Borrado,mapear_elementos_a_objetos
import os
import json
from apps.utils.file_util import path_join

CARPETA_DESCARGAS = "./descargas"


class Builder:
    @staticmethod
    def obtener_instancia(yeoman_handler):
        return RepositoryBinder(yeoman_handler)


class Path:

    def __init__(self, data):
        self.path_desde = data["path_desde"]
        self.path_hasta = data["path_hasta"]

    def to_map(self):
        return {"path_desde": self.path_desde, "path_hasta": self.path_hasta}


class Repositorio:
    def __init__(self, data):
        self.habilitado = data.get("habilitado", True)
        self.nombre = data["nombre"]
        self.url = data["url"]
        self.paths = mapear_elementos_a_objetos(data["paths"], Path)

class RepositoryBinder(Plugin):

    def __init__(self, yeoman_handler):

        with open(path_join(os.path.dirname(__file__).replace(os.getcwd(),""),"configuracion.json")[1:]) as f:
            data = json.load(f)

        super().__init__(yeoman_handler, data)

        self.repositorios = mapear_elementos_a_objetos(data["repositorios"], Repositorio)

    def _descargar(self, repo):
        url = self.yeoman_handler.reemplazar_variables(repo.url)

        os.system('git clone ' + url + ' ' +
                  path_join(CARPETA_DESCARGAS, repo.nombre)+" >/dev/null 2>&1")
    def _copiar_archivos(self, repo):

        for ruta in repo.paths:

            ruta.path_desde = path_join(CARPETA_DESCARGAS, ruta.path_desde)

            #BORRO EL CONTENIDO PARA QUE LO REEMPLACE POR LO DE DESCARGAS

            borrado = Borrado({"path": ruta.path_hasta})
            borrado.aplicar(self.yeoman_handler.configuracion.root_path, self.yeoman_handler)

            copia = Copia(ruta.to_map())
            copia.aplicar(self.yeoman_handler.configuracion.root_path, self.yeoman_handler)

    def _borrar(self, repo):

        borrado = Borrado({"path": repo.nombre})
        borrado.aplicar(CARPETA_DESCARGAS, self.yeoman_handler)

    def aplicar(self, path_proyecto):
        return

    def ejecutar_menu(self):

        self.yeoman_handler.log("APLICANDO REPOSITORY BINDER ...")

        for repo in filter(lambda r: r.habilitado, self.repositorios):
            # self._borrar(repo)
            try:
                self._descargar(repo)
            except Exception as _:
                pass

            self._copiar_archivos(repo)
            # self._borrar(repo)
