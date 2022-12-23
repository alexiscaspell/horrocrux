import os
import shutil
import glob
import re
import json
import horrocrux.utils.file_util as fu
from horrocrux.utils.logger_util import get_logger
from horrocrux.models.app_model import AppModel,model_metadata
from enum import Enum
from typing import List,Dict

logger = get_logger(__name__)

class TipoVariable(Enum):
    literal="literal"
    codigo="codigo"

@model_metadata({"nombre":str,"valor":str,"tipo":TipoVariable})
class Variable(AppModel):
    def __init__(self,var_spec:Dict):
        self.nombre = var_spec["nombre"]
        self.valor = var_spec["valor"]
        self.tipo = var_spec.get("tipo",TipoVariable.literal)
        self.dependencias = []

    # def obtener_valor(self,config):
    #     if self.valor is None:
    #         return None

    #     valor = self.valor.replace("@@" + self.nombre, str(self.configuracion.variables[self.nombre].obtener_valor()))

    #     if self.tipo==TipoVariable.codigo:
    #         return eval(valor)

class ConfiguracionYeoman() :

    def __init__(self,root_path):

        with open(fu.path_join(root_path, "/generators/configuracion.json")) as f:
            data = json.load(f) #(with path)

        self.plugins = data["plugins"]

        self.ejecutar_plugin_principal_al_inicio = data.get("ejecutar_plugin_principal_al_inicio",True)

        self.saltar_pre_validaciones = data.get("saltar_pre_validaciones",False)

        self.root_path = root_path

        self.path_plugin_principal = fu.path_join(root_path, data["path_plugin_principal"])

        self.path_template_principal = fu.path_join(self.path_plugin_principal,"/proyecto")

        self.plugins_obligatorios = data.get("plugins_obligatorios", [])

        self.variables = {}

        for v in data.get("variables",[]):

            nombre_variable = v if isinstance(v,str) else v["nombre"]
            valor = getattr(self, nombre_variable) if isinstance(v,str) else getattr(self, v["valor"])
            tipo = "literal" if isinstance(v,str) else v.get("tipo","literal")

            self.agregar_variable(nombre_variable,valor,tipo=tipo)

            

    @property
    def path_proyecto(self):
        path = self.obtener_variable("path_proyecto","")
        return path
    
    @path_proyecto.setter
    def path_proyecto(self, un_path):
        self.agregar_variable("path_proyecto",un_path)

    @property
    def nombre_proyecto(self):
        nombre = self.obtener_variable("nombre_proyecto","")
        return nombre
    
    @nombre_proyecto.setter
    def nombre_proyecto(self, un_nombre):
        self.agregar_variable("nombre_proyecto",un_nombre)

    def agregar_variable(self,variable:str,valor:str,tipo:TipoVariable=TipoVariable.literal):
        if variable is None:
            return

        self.variables.pop(variable,None)

        for v in self.variables.values():
            if v.valor is None:
                continue
            if "@@"+variable in v.valor and variable not in v.dependencias:
                v.dependencias.append(variable)
            
        objeto_variable = Variable.from_dict({"nombre":variable,"valor":valor,"tipo":tipo})
        self.variables.update({variable:objeto_variable})

    def _obtener_variable(self,variable:str,variables_a_evaluar:List[str],default:str,tipo:TipoVariable):
        objeto_variable = self.variables.get(variable,Variable.from_dict({"nombre":variable,"valor":default,"tipo":tipo}))

        if objeto_variable.valor is None:
            return ""

        valor = objeto_variable.valor

        for v in variables_a_evaluar:
            variables_a_evaluar.remove(self.variables[v].nombre)
            if self.variables[v].valor is None:
                continue
            valor = valor.replace("@@"+v,self._obtener_variable(v,variables_a_evaluar,default=default,tipo=self.variables[v].tipo))

        if objeto_variable.tipo==TipoVariable.codigo:
            valor = eval(valor)

        return valor

    def _obtener_dependencias(self,depen):

        dependencia = self.variables.get(depen)

        if dependencia is None:
            return []

        if len(dependencia.dependencias)==0:
            return [dependencia.nombre]

        dependencias=[]

        for d in dependencia.dependencias:
            dependencias = dependencias+_obtener_dependencias(d)

        return dependencias

    def obtener_dependencias(self,variable:Variable):
        dependencias=[]

        for d in variable.dependencias:
            dependencias=dependencias+self._obtener_dependencias(d)

        return dependencias
            
    def obtener_variable(self,variable:str,default:str=None,tipo:TipoVariable=TipoVariable.literal):
        objeto_variable = self.variables.get(variable,Variable.from_dict({"nombre":variable,"valor":default,"tipo":tipo}))

        dependencias = self.obtener_dependencias(objeto_variable)

        # if len(dependencias)!=len(set(dependencias)):
        #     raise RuntimeError("Dependencias circulares entre variables")

        return self._obtener_variable(variable,dependencias,default,tipo)


class Yeoman:

    def __init__(self,path_principal:str=None):
        # Calling the super constructor is important so our generator is correctly set up
        self.path_principal = path_principal if path_principal is not None else self.default_root_path()
        self.configuracion = ConfiguracionYeoman(self.root_path())
        # super(args, opts)

    def root_path(self):
        '''Es el directorio root desde el cual se agarraran los plugins o la config del generador'''
        return self.path_principal

    def default_root_path(self):
        '''Es el directorio root default en caso de no encontrarse algo en root_path'''
        return "files/"

    def log(self,texto):
        '''Es al que llama el propio generador para loguear'''
        #ACTUALMENTE NO SE LOGUEA NADA!
        return
        # logger.info(texto)
    
    def copiar_contenido(self,path_contenido, path_sumidero):
        '''Copia el contenido de un archivo a otro'''
        self.copiar_archivo(path_contenido, path_sumidero, True)

    def borrar_archivo(self,path_a_borrar):
        '''Borra un archivo o directorio'''
        fu.delete_file(path_a_borrar)

    def copiar_archivo(self,path_desde, path_hasta, reemplazar_si_existe = True,mover=False):
        '''Copia un archivo de un path a otro con la opcion de reemplazarlo si ya existe'''
        fu.copy_file(path_desde,path_hasta,reemplazar_si_existe,mover)

    def apendear_archivo(self,path_archivo, funcion_apendeo):
        '''Agrega nuevo contenido a un archivo segun la funcion de apendeo'''
        content = self.leer_archivo(path_archivo)

        newContent = funcion_apendeo(content)

        with open(path_archivo,"w") as f:
            f.writelines(newContent)

    def listar_archivos(self,dir):
        '''Lista todos los archivos del directorio recursivamente'''
        return fu.list_files(dir)

    def leer_archivo(self,path):
        '''Retorna el contenido de un archivo'''
        with open(path) as file:
            s = file.read()
        return s

    def reemplazar_texto(self,regex, texto, contenido):
        '''Realiza un replace del string texto por el filtro de regex reemplazandolo por contenido'''
        return re.sub(regex,texto,contenido)

    def reemplazar_variables(self,un_string):
        '''Reemplaza una variable del generador de proyectos'''
        un_string = str(un_string)

        variables_ordenadas = [v for v in self.configuracion.variables]
        variables_ordenadas.sort()
        variables_ordenadas.reverse()

        for v in variables_ordenadas:
            if self.configuracion.variables[v].valor is None:
                continue
            if v=='nombre-proyecto':
                lrpm = 9
            un_string = un_string.replace("@@" + v, str(self.configuracion.obtener_variable(v)))
        
        return un_string
    

    def mover_archivo(self,path_desde, path_hasta):
        '''Mueve un archivo desde un path a otro (copiar y borrar)'''
        self.copiar_archivo(path_desde,path_hasta,reemplazar_si_existe=True,mover=True)

    def es_archivo(self,dir):
        '''Detecta si un path es un archivo'''
        return not self.es_directorio(dir)

    def es_directorio(self,dir):
        '''Detecta si un path es un directorio'''
        return fu.is_dir(dir)

    def renombrar_archivos(self,dir, from_rename, to_rename):
        '''Renombra recursivamente todos los archivos con nombre from_rename a to_rename'''
        for filepath in self.listar_archivos(dir):
            os.rename(filepath,re.sub(from_rename,to_rename,filepath))

    def reemplazar_contenido(self,paths, regEx, texto):
        '''Reemplaza recursivamente el contenido de todos los archivos que se encuentren en paths'''

        for path_a_reemplazar in paths:
            for filepath in self.listar_archivos(path_a_reemplazar):
                if self.es_directorio(filepath):
                    continue
                try:
                    s = self.leer_archivo(filepath)
                    s = self.reemplazar_texto(regEx,texto,s)

                    with open(filepath, "w") as file:
                        file.write(s)
                except UnicodeDecodeError as _:
                    pass

    def indice_ocurrencia_texto(self,un_texto,regex,primera_ocurrencia=True):
        '''Retorna el indice y la longitud de la ocurrencia de regex en un_texto, si primera_ocurrencia=False entonces busca la ultima'''
        ultima = None

        for x in re.finditer(regex, un_texto):
            if primera_ocurrencia:
                return x.span()[0] , x.span()[1] - x.span()[0] 
            ultima = x.span()

        return ultima.span()[0] , ultima.span()[1] - ultima.span()[0] if ultima else None

