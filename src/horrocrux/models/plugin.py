import os
from horrocrux.models.yeoman import Yeoman
import re
from horrocrux.utils.file_util import path_join
import json
from horrocrux.models.menu import Menu
from horrocrux.models.app_model import AppModel,model_metadata

class Copia :

    def __init__(self,data):

        self.path_desde = data["path_desde"]
        self.path_hasta = data["path_hasta"]
        self.mover = data.get("mover", False)
    

    def aplicar(self,path_proyecto, yeoman_handler):

        path_desde = path_join(yeoman_handler.reemplazar_variables(self.path_desde))
        path_hasta = path_join(yeoman_handler.reemplazar_variables(path_join(path_proyecto, self.path_hasta)))

        if (self.mover):
            yeoman_handler.mover_archivo(path_desde, path_hasta)
            return
        
        yeoman_handler.copiar_archivo(path_desde, path_hasta, True)
    
class Borrado :

    def __init__(self,data):

        self.path = data["path"]

    def aplicar(self,path_proyecto, yeoman_handler):

        path_a_borrar = yeoman_handler.reemplazar_variables(path_join(path_proyecto, self.path))

        yeoman_handler.borrar_archivo(path_a_borrar)
    
class Merge :

    def __init__(self,data):

        self.archivo_desde = data["archivo_desde"]
        self.archivo_hasta = data["archivo_hasta"]
        self.despues_de = data.get("despues_de", None)
        self.antes_de = data.get("antes_de", None)
        self.separador = data.get("separador", "")
        self.reemplazar = data.get("reemplazar", True)
        # self.texto_desde = data.get("texto_desde",None)
        # self.texto_hasta = data.get("texto_hasta",None)
    

    def aplicar(self,path_proyecto, yeoman_handler:Yeoman):
        contenido = yeoman_handler.leer_archivo(yeoman_handler.reemplazar_variables(self.archivo_desde))

        # indice_desde,longitud_desde = yeoman_handler.indice_ocurrencia_texto(contenido,self.texto_desde) if self.texto_desde else 0,0
        # indice_desde = indice_desde+longitud_desde-1
        # indice_desde = indice_desde if indice_desde>0 else 0

        # indice_hasta,_ = yeoman_handler.indice_ocurrencia_texto(contenido,self.texto_hasta,primera_ocurrencia=False) if self.texto_hasta else len(contenido)-1,None
        # indice_hasta = indice_hasta if indice_hasta>0 else 0

        # contenido = contenido[indice_desde+longitud_desde-1:indice_hasta]

        apendear_antes = self.despues_de is None
        separador = self.separador

        #SE REEMPLAZAN LAS VARS DE REGEX
        regex = self.antes_de if apendear_antes else self.despues_de
        regex = yeoman_handler.reemplazar_variables(regex)

        hay_que_reemplazar = self.reemplazar

        def f(some_regex,hay_que_reemplazar):
            def f_hija (content,regex=some_regex,reemplazar=hay_que_reemplazar):

                if (regex == "EOF"):
                    regex = "@@ENDOFFILE@@"
                    content = content + "\n" + regex
                    reemplazar = True
                

                # regEx = new RegExp(regex, 'g')

                matches = re.findall(regex,content)

                primer_match = "" if reemplazar else (matches[0] if matches is not None and len(matches) > 0 else "")

                valor_a_reemplazar = contenido + separador + primer_match if apendear_antes else primer_match + separador + contenido

                newContent=re.sub(regex,valor_a_reemplazar,str(content))

                return newContent

            return f_hija
        

        yeoman_handler.apendear_archivo(path_join(path_proyecto, yeoman_handler.reemplazar_variables(self.archivo_hasta)), f(regex,hay_que_reemplazar))
    


REEMPLAZO_CARPETA = "nombre"
REEMPLAZO_TEXTO = "contenido"
REEMPLAZO_CARPETA_Y_TEXTO = "todo"

class Reemplazo :

    def __init__(self,data):

        self.paths = data["paths"]
        self.texto = data["texto"]
        self.regex = data["regex"]
        self.tipo = data.get("tipo", REEMPLAZO_CARPETA_Y_TEXTO)
    

    def aplicar(self,path_proyecto, yeoman_handler):

        regEx = yeoman_handler.reemplazar_variables(self.regex)

        paths = []

        for p in self.paths:
            paths.append(yeoman_handler.reemplazar_variables(path_join(path_proyecto, p)))
        

        if (self.tipo == REEMPLAZO_CARPETA_Y_TEXTO or self.tipo == REEMPLAZO_TEXTO):
            yeoman_handler.reemplazar_contenido(paths, regEx, yeoman_handler.reemplazar_variables(self.texto))

        if (self.tipo == REEMPLAZO_CARPETA_Y_TEXTO or self.tipo == REEMPLAZO_CARPETA):
            for p in paths:
                yeoman_handler.renombrar_archivos(p, yeoman_handler.reemplazar_variables(self.regex), yeoman_handler.reemplazar_variables(self.texto))

class Builder:
    @staticmethod
    def obtener_instancia(yeoman_handler,path):
        with open(path_join(path,"configuracion.json")) as f:
            data = json.load(f)

        return Plugin(yeoman_handler,data)
            
@model_metadata({})
class PluginSpec(AppModel) :

    def __init__(self, data):
        self.descripcion = data["descripcion"]

        self.variables = data.get("variables", [])

        self.menues = data.get("menues", [])

        self.copias = data.get("copias", [])
        self.merges = data.get("merges", [])
        self.reemplazos = data.get("reemplazos", [])
        self.borrados = data.get("borrados", [])

@model_metadata({})
class Plugin(AppModel) :

    def __init__(self,yeoman_handler, data):
        self.yeoman_handler = yeoman_handler

        self.descripcion = data["descripcion"]

        self.variables = data.get("variables", [])

        self._cargar_variables(self.variables, yeoman_handler)

        self.menues = mapear_elementos_a_objetos(data.get("menues", []), Menu)

        self.copias = mapear_elementos_a_objetos(data.get("copias", []), Copia)
        self.merges = mapear_elementos_a_objetos(data.get("merges", []), Merge)
        self.reemplazos = mapear_elementos_a_objetos(data.get("reemplazos", []), Reemplazo)
        self.borrados = mapear_elementos_a_objetos(data.get("borrados", []), Borrado)
    

    def _cargar_variables(self,variables, yeoman_handler):
        for v in variables:
            yeoman_handler.configuracion.agregar_variable(v["nombre"],v["valor"],tipo=v.get("tipo","literal"))

    def ejecutar_menu(self):
        for m in self.menues:
            m.ejecutar(self.yeoman_handler)

    def aplicar(self,path_proyecto):

        for c in self.copias:
            c.aplicar(path_proyecto, self.yeoman_handler)
        

        for b in self.borrados:
            b.aplicar(path_proyecto, self.yeoman_handler)
        

        for m in self.merges:
            m.aplicar(path_proyecto, self.yeoman_handler)
        

        for r in self.reemplazos:
            r.aplicar(path_proyecto, self.yeoman_handler)

    
def mapear_elementos_a_objetos(lista, clase):
    objetos = []

    for e in lista:
        objetos.append(clase(e))

    return objetos