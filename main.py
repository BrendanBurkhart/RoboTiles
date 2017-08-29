"""
Simple robot programming as learning game/demo
"""

from kivy.config import Config

# Set window size to 600x648 (width x height)
# Prevent window from being resized
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '648')

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty


class Menu(Screen):
    """
    Main menu screen

    Has edit code, instructions and options buttons
    """
    def edit_code(self):
        """
        Switch to edit screen
        """
        self.manager.current = 'EditCode'

    def instructions(self):
        """
        Switch to instructions screen
        """
        self.manager.current = 'Instructions'

    def test_code(self):
        """
        Switch to test screen
        """
        self.manager.current = 'TestCode'

    def edit_board(self):
        """
        Switch to board editing screen
        """
        self.manager.current = 'EditBoard'

    def options(self):
        """
        Switch to more options screen
        """
        self.manager.current = 'Options'


class EditCode(Screen):
    """
    Editor for Python robot code
    """

    code_file = StringProperty('')
    template_file = StringProperty('')

    def menu(self):
        """
        Switch to main menu, and save editor contents to file
        """
        self.save_code()

        self.manager.current = 'Menu'

    def test_code(self):
        """
        Switch to test screen and save editor contents to file
        """
        self.save_code()

        self.manager.current = 'TestCode'

    def reset_code(self):
        """
        Reset code to default template
        """
        input_field = self.get_input_field()

        with open(str(self.template_file), 'r') as template:
            input_field.text = template.read()

    def on_pre_enter(self, *args):
        """
        Overriden method from `Screen`, called before this
         screen is switched to. Used here to load
         current code into editor.
        """
        super(EditCode, self).on_pre_enter(*args)

        self.get_code()

    def save_code(self):
        """
        Get the code from the editor and save it to disk
        """
        input_field = self.get_input_field()

        code = input_field.text

        code = code.replace('\t', '    ')

        with open(str(self.code_file), 'w') as path:
            path.write(code)

    def get_code(self):
        """
        Get the code file and set editor contents to that code
        """
        input_field = self.get_input_field()

        with open(str(self.code_file), 'r') as path:
            code = path.read()

        input_field.text = code

    def get_input_field(self):
        """
        Get reference to the editor
        """
        return self.ids.input_field


class Instructions(Screen):
    """
    Instruction/directions screen

    Accessible from main menu, provides basic overview of funtionality
    """

    instructions_file = StringProperty('')

    def __init__(self, *args, **kwargs):
        super(Instructions, self).__init__(*args, **kwargs)

        Clock.schedule_once(self._init)

    def _init(self, dt=0):
        """
        Second stage of init

        `dt` is argument for Clock scheduling, leave as default.
        """
        rst_doc = self.ids.rst_doc

        rst_doc.text = self.load_contents(self.instructions_file)

    def menu(self):
        """
        Switch to main menu screen
        """
        self.manager.current = 'Menu'

    def load_contents(self, instructions_file: str):
        """
        Get contents of instruction file

        :Args:
           - `instrcutions_file`: Name of file to load instructions from as string

        :Returns: Contents of instruction file as string
        """
        with open(instructions_file, 'r') as instructions:
            return instructions.read()


class Options(Screen):
    """
    More options screen, accessed from main menu, contains
     additional buttons that don't fit on main menu.

    Has return to main menu, test code button.
    """

    def menu(self):
        """
        Switch to main menu
        """
        self.manager.current = 'Menu'

    def test_code(self):
        """
        Switch to test screen
        """
        self.manager.current = 'TestCode'

    def edit_board(self):
        """
        Switch to board editing screen
        """
        self.manager.current = 'EditBoard'


class RoboTilesApp(App):
    """
    Kivy app class
    """

    def build(self):
        # Set background window color for all screens
        Window.clearcolor = (0.8125, 0.796875, 0.78125, 1)

        return self.root

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    RoboTilesApp().run()
