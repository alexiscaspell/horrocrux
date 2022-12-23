from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget,DropdownList,Label,FileBrowser,PopUpDialog
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import sys
from horrocrux.models.app_model import AppModel,model_metadata
import os

class PluginModel(object):
    def __init__(self,generador):
        # Create a database in RAM
        self.generador = generador

        self.path_proyecto = generador.configuracion.path_proyecto

        self.form_data={"path_proyecto":self.path_proyecto,"__path_seleccionado__":0,"__plugin_a_agregar__":0,"__plugin_seleccionado__":0,"nombre_proyecto":generador.configuracion.nombre_proyecto}

        # Current plugin when editing.
        self.current_id = None

    def add(self, plugin_index):

        if plugin_index==0:
            return

        plugin_index-=1

        self.generador.seleccionados.append(self.generador.obtener_plugins()[plugin_index])

    def get_summary(self):
        return [(s.descripcion,i) for i,s in enumerate(self.generador.seleccionados)]

    def get_plugin(self, plugin_index):
        return self.generador.seleccionados[int(plugin_index)]

    def get_current_plugin(self):
        if self.current_id is None:
            return None
        else:
            return self.get_plugin(self.current_id)

    def update_path_proyecto(self,nuevo_path):
        self.form_data["path_proyecto"]=nuevo_path

    def delete_plugin(self, plugin_index):
        self.generador.seleccionados.pop(plugin_index)


class MenuView(Frame):
    def __init__(self, screen, model):
        super(MenuView, self).__init__(screen,
                                       screen.height * 2 // 3,
                                       screen.width * 2 // 3,
                                       on_load=self._reload_list,
                                       data=model.form_data,
                                       hover_focus=True,
                                       can_scroll=False,
                                       title="Horrocrux")
        # Save off the model that accesses the plugins database.
        self._model = model

        self._build_button = Button("Build", self._build)
        self._edit_button = Button("Edit", self._edit)
        self._delete_button = Button("Delete", self._delete)

        #################### LAYOUT 1#######################
        layout = Layout([1,50,1])
        self.add_layout(layout)

        layout.add_widget(Label("CONFIGURACION",align="^"), 1)

        layout.add_widget(
            Text(label="Nombre Proyecto:",
                 name="nombre_proyecto",
                 on_change=self._on_change), 1)

        self._list_view_path = DropdownList(
        [(model.form_data["path_proyecto"],0),("Cambiar",1)],
        label="Path Proyecto", name="__path_seleccionado__", on_change=self._edit_path_proyecto)
        layout.add_widget(self._list_view_path, 1)

        layout.add_widget(DropdownList(
        [("Ninguno",0)]+[(p.descripcion,i+1) for i,p in enumerate(self._model.generador.obtener_plugins())],
        label="Plugins", name="__plugin_a_agregar__", on_change=self._on_change),1)


        layout.add_widget(Divider(height=2), 1)
        layout.add_widget(Label("PLUGINS SELECCIONADOS",align="^",height=2), 1)

        self._list_view = DropdownList(model.get_summary(),label="Plugins", name="__plugin_seleccionado__", on_change=self._on_pick)

        layout.add_widget(self._list_view,1)

        layout.add_widget(Divider(height=3), 1)

        #################### LAYOUT 2#######################
        layout2 = Layout([1, 1, 1, 1,1])

        self.add_layout(layout2)
        layout2.add_widget(Button("Add", self._add), 0)

        layout2.add_widget(self._edit_button, 1)
        layout2.add_widget(self._delete_button, 2)

        layout2.add_widget(self._build_button, 3)

        layout2.add_widget(Button("Quit", self._quit), 4)

        self.fix()
        self._on_pick()
        self.set_theme("bright")

    def _edit_path_proyecto(self):
        self.save()
        if self._model.form_data["path_proyecto"]==self._model.path_proyecto:
            self._model.path_proyecto=None
            self._model.form_data["__path_seleccionado__"]=0
            self.save()
            raise NextScene("elegir_path")
        else:
            self._model.path_proyecto=self._model.form_data["path_proyecto"]
            self._model.form_data["__path_seleccionado__"]=0
            self._list_view_path._options = [(self._model.path_proyecto,0),("Cambiar",1)]
            self.save()

    def _build(self):

        mensaje = f"El proyecto {self._model.form_data['nombre_proyecto']} se ha realizado con exito!"
        try:
            self._model.generador.construir_proyecto()
        except Exception as e:
            mensaje = str(e)
            pass

        self._scene.add_effect(
            PopUpDialog(self._screen, mensaje, ["OK"]))

    def _on_change(self):
        self.save()
        for key, value in self.data.items():
            if key not in self._model.form_data or self._model.form_data[key] != value:
                self._model.form_data[key]=value
                if key in self._model.generador.configuracion.variables:
                    self._model.generador.configuracion.agregar_variable(key,value)
                break

    def _on_pick(self):
        self._edit_button.disabled = self._list_view.value is None
        self._delete_button.disabled = self._list_view.value is None

    def _reload_list(self, new_value=None):
        self._list_view._options = self._model.get_summary()

    def _add(self):
        self.save()
        self._model.add(self.data["__plugin_a_agregar__"])
        self._reload_list()

    def _edit(self):
        self.save()
        self._model.current_id = self.data["__plugin_seleccionado__"]
        raise NextScene("editar_plugin")

    def _delete(self):
        self.save()
        self._model.delete_plugin(self.data["__plugin_seleccionado__"])
        self._reload_list()

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")

class FileSystemFrame(Frame):
    def __init__(self, screen,model):
        # super(FileSystemFrame, self).__init__(
        #     screen, screen.height, screen.width, has_border=False, name="My Form")

        super(FileSystemFrame, self).__init__(screen,
                                          screen.height * 2 // 3,
                                          screen.width * 2 // 3,
                                          hover_focus=True,
                                          can_scroll=False,
                                          title="Seleccion de path de proyecto",
                                          reduce_cpu=True)

        # Create the (very simple) form layout...
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)

        self._model = model

        # Now populate it with the widgets we want to use.
        self._details = Text()
        self._details.disabled = True
        self._details.custom_colour = "field"
        self._list = FileBrowser(Widget.FILL_FRAME,
                                 os.path.abspath("."),
                                 name="mc_list",
                                 on_select=self.popup,
                                 on_change=self.details)
        layout.add_widget(Label("Local disk browser"))
        layout.add_widget(Divider())
        layout.add_widget(self._list)
        layout.add_widget(Divider())
        layout.add_widget(self._details)
        layout.add_widget(Label("Press Enter to select, tab to confirm or `q` to quit."))

        # Prepare the Frame for use.
        self.fix()

        self.set_theme("bright")


    def popup(self):
        # Just confirm whenever the user actually selects something.
        self._scene.add_effect(
            PopUpDialog(self._screen, "You selected: {}".format(self._list.value), ["OK"]))

    def details(self):
        # If python magic is installed, provide a little more detail of the current file.
        if self._list.value:
            if os.path.isdir(self._list.value):
                self._details.value = "Directory"
            elif os.path.isfile(self._list.value):
                try:
                    self._details.value = magic.from_file(self._list.value)
                except NameError:
                    self._details.value = "File (run 'pip install python-magic' for more details)"
        else:
            self._details.value = "--"

    def process_event(self, event):
        # Do the key handling for this Frame.
        if isinstance(event, KeyboardEvent):
            if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
                raise NextScene("main")
            if event.key_code in [Screen.KEY_TAB]:
                self._model.update_path_proyecto(self._list.value)
                raise NextScene("main")

        # Now pass on to lower levels for normal handling of the event.
        return super(FileSystemFrame, self).process_event(event)


class PluginView(Frame):
    def __init__(self, screen, model):
        super(PluginView, self).__init__(screen,
                                          screen.height * 2 // 3,
                                          screen.width * 2 // 3,
                                          hover_focus=True,
                                          can_scroll=False,
                                          title="Configuracion de plugin",
                                          reduce_cpu=True)

        # Save off the model that accesses the plugins database.
        self._model = model

        # Create the form for displaying the list of plugins.
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        self.menu_layout = layout

        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 3)
        self.fix()
        self.set_theme("bright")

    def reset(self):

        menues = self._model.get_current_plugin().menues if self._model.get_current_plugin() else []

        self.menu_layout.clear_widgets()

        for m in menues:
            self.menu_layout.add_widget(Text(m.texto, m.resultado))

        self.fix()

        # Do standard reset to clear out form, then populate with new data.
        super(PluginView, self).reset()

        self.set_theme("bright")

        self.menues = {m.resultado:m for m in menues}

        self.data = {m.resultado:self._model.generador.reemplazar_variables(m.default) if m.resultado not in self._model.generador.configuracion.variables else self._model.generador.configuracion.obtener_variable(m.resultado) for m in menues}

    def _ok(self):
        self.save()

        for key,value in self.data.items():
            menu = self.menues[key]
            menu.opcion_seleccionada = value

        self._model.get_current_plugin().ejecutar_menu()
        raise NextScene("main")

    @staticmethod
    def _cancel():
        raise NextScene("main")



def demo(screen, scene,generador):
    scenes = []

    plugins = PluginModel(generador)

    scenes.append(Scene([MenuView(screen, plugins)], -1, name="main"))
    scenes.append(Scene([PluginView(screen, plugins)], -1, name="editar_plugin"))
    scenes.append(Scene([FileSystemFrame(screen,plugins)], -1, name="elegir_path"))

    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

def ejecutar_menu(generador_proyecto):
    last_scene = None
    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene,generador_proyecto])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene

@model_metadata({})
class Menu(AppModel) :

    def __init__(self,data):

        self.resultado = data["resultado"]
        self.texto = data.get("texto", "Ingrese el valor de " + self.resultado)
        self.default = data["default"]
        self.opcion_seleccionada=None

    def ejecutar(self,yeoman_handler):
        self.opcion_seleccionada = self.opcion_seleccionada if self.opcion_seleccionada else self.default
        self.opcion_seleccionada = yeoman_handler.reemplazar_variables(self.opcion_seleccionada)
        
        yeoman_handler.configuracion.agregar_variable(self.resultado,self.opcion_seleccionada)