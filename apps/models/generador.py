from apps.models.yeoman import Yeoman
from apps.models.plugin import Plugin
from typing import List, Dict
from apps.utils.file_util import path_join,is_dir,delete_file,path_exists
from apps.models.plugin import Builder
from apps.models.app_model import AppModel,model_metadata
import ntpath

@model_metadata({})
class GeneradorProyectoSpec(AppModel):
    def __init__(self,generador_spec:Dict):
        self.id = generador_spec.get("id","")
        self.path_plugin_principal = generador_spec.get("path_plugin_principal","")
        self.ejecutar_plugin_principal_al_inicio = generador_spec.get("ejecutar_plugin_principal_al_inicio",True)
        self.saltar_pre_validaciones = generador_spec.get("saltar_pre_validaciones",True)
        self.plugins = generador_spec.get("plugins",[])
        self.plugins_obligatorios = generador_spec.get("plugins_obligatorios",["repository-binder","variables"])
        self.variables = generador_spec.get("variables",["path_proyecto","nombre_proyecto"])

@model_metadata({"generador":GeneradorProyectoSpec})
class CreacionProyectoSpec(AppModel):
    def __init__(self,creacion_spec:Dict):
        self.generador = creacion_spec["generador"]
        self.proyecto = creacion_spec["proyecto"]
        self.id = creacion_spec.get("id",None)
        super().__init__()

    # METODO QUE SE EJCUTA CON EL INICIO DEL COMANDO
class GeneradorProyecto(Yeoman):

    def __init__(self, *args):
        '''
        arg0 : nombre_proyecto,
        arg1 : carpeta,
        arg2 : path_principal
        '''

        nombre_proyecto, carpeta = args[0],args[1] 

        path_principal = args[2] if len(args)>2 and is_dir(args[2]) else None

        super().__init__(path_principal)

        if (nombre_proyecto is None or nombre_proyecto == "") and not self.configuracion.saltar_pre_validaciones:
            raise ValueError('Tirame un nombre de proyecto muerto!!')

        if (carpeta is None or carpeta == ""):
            carpeta = self.root_path()

        self.update_nombre_y_path(nombre_proyecto,carpeta)

        self.plugins_obligatorios = self.get_plugins_obligatorios()

        self.seleccionados = self.plugins_obligatorios+[]
        
        self.plugin_principal = None
        self.plugin_principal = self.get_plugin_principal()

    def update_nombre_y_path(self,nombre_proyecto,carpeta):
        '''Actualiza el nombre de proyecto y su carpeta'''
        self.configuracion.nombre_proyecto = nombre_proyecto
        self.configuracion.path_proyecto = carpeta
        # self.configuracion.agregar_variable(
        #     "nombre_proyecto", self.configuracion.nombre_proyecto)
        # self.configuracion.agregar_variable(
        #     "path_proyecto", self.configuracion.path_proyecto)

    def obtener_plugin_por_path(self, path):
        '''Crea un nuevo plugin a traves del path'''

        package = str(path).replace("/", ".")+".index"

        try:
            i = __import__(package, fromlist=[''])

            return i.Builder.obtener_instancia(self)
        except Exception as _:
            return Builder.obtener_instancia(self, path)

    def _obtener_plugins(self,plugin_paths):
        plugins = []

        for p in plugin_paths:

            head, tail = ntpath.split(p)

            if not tail or tail=="":
                tail,head=ntpath.basename(head)

            if not head or head=="":
                head= path_join(self.configuracion.root_path, "/plugins/")

            try:
                plugin = self.obtener_plugin_por_path(path_join(head,tail))
            except Exception as _:
                plugin = self.obtener_plugin_por_path(path_join(self.default_root_path(),"plugins",tail))

            plugins.append(plugin)

        return plugins

    def obtener_plugins(self):
        '''Retorna todos los plugins configurados en la config del generador'''
        return self._obtener_plugins(self.configuracion.plugins)

    def get_plugins_obligatorios(self):
        '''Retorna todos los plugins obligatorios configurados en la config del generador'''
        return self._obtener_plugins(self.configuracion.plugins_obligatorios)

    def get_plugin_principal(self):
        '''Retorna el plugin principal o base del generador'''
        return self.obtener_plugin_por_path(self.configuracion.path_plugin_principal) if self.plugin_principal is None else self.plugin_principal

    def construir_proyecto(self):
        '''Construye el proyecto con los plugins seteados anteriormente'''

        path_proyecto = path_join(self.configuracion.obtener_variable("path_proyecto"),self.configuracion.obtener_variable("nombre_proyecto"))

        self.configuracion.path_proyecto = path_proyecto

        seleccionados = []

        for s in self.seleccionados:
            if s in seleccionados:
                continue
            seleccionados.append(s)

        # seleccionados = list(set(self.seleccionados))

        plugin_del_proyecto = self.get_plugin_principal()

        seleccionados = [plugin_del_proyecto] + \
            seleccionados if self.configuracion.ejecutar_plugin_principal_al_inicio else seleccionados + \
            [plugin_del_proyecto]

        try:
            #EJECUTO TODOS LOS MENUES
            for p in seleccionados:
                p.ejecutar_menu()

            self.log("COPIANDO CONTENIDO DE " + self.configuracion.path_template_principal +
                    " A " + path_proyecto + " ...")

            self.copiar_contenido(self.configuracion.path_template_principal, path_proyecto)

            #EJECUTO TODOS LOS PLUGINS
            for p in seleccionados:
                self.log(f"APLICANDO PLUGIN {p.descripcion} AL PATH " + path_proyecto)
                p.aplicar(path_proyecto)

        except Exception as e:
            #EN CASO DE ERROR BORRO PROYECTO
            if path_exists(path_proyecto):
                delete_file(path_proyecto)
            raise e
