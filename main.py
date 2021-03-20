# All the import statements needed in current version or upcoming version
import kivy
from kivy.metrics import sp
from kivy.properties import StringProperty, NumericProperty, OptionProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.utils import get_color_from_hex
from kivy.config import Config
from kivy.core.window import Window
import re
from fractions import Fraction

kivy.require('2.0.0')

# // Search for resources in project root file (optional)
Config.write()
kivy.resources.resource_add_path("./")


# // Sets status bar color to white on android
# // Currently, not working properly on modified ROMs like MIUI
def white_status_bar():
    from android.runnable import run_on_ui_thread

    @run_on_ui_thread
    def _white_status_bar():
        from jnius import autoclass
        WindowManager = autoclass('android.view.WindowManager$LayoutParams')
        Color = autoclass('android.graphics.Color')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        window = activity.getWindow()
        window.clearFlags(WindowManager.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(WindowManager.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
        window.setStatusBarColor(Color.WHITE)
    _white_status_bar()


class MatrixValue(TextInput):
    def __init__(self, **kwargs):
        super(MatrixValue, self).__init__(**kwargs)
        self.background_normal = ''
        self.multiline = False
        self.font_size = sp(20)
        self.background_color = get_color_from_hex('#69B6BA')
        self.foreground_color = [1, 1, 0.8, 1]


# Development of grid layout that contains all the units of matrix
class MatrixGrid(GridLayout, BoxLayout):
    order = NumericProperty(0)

    # Function to make Matrix view as per the provided order
    def on_order(self, *args):

        order = int(self.order)
        MDApp.get_running_app().root.ids.display_box.text = ''
        self.clear_widgets()
        self.cols = order
        self.rows = order

        for i in range(1, order + 1):
            for k in range(1, order + 1):
                set_id = 'a' + str(i) + str(k)
                text_input = MatrixValue()
                text_input.id = set_id
                self.add_widget(text_input)


# // Our main App
# // All the initiations, exchanges and processes done here
class MatrixCalculator(MDApp):
    def __init__(self, **kwargs):
        self.title = "Matrix Calculator"
        self.theme_cls.theme_style = "Light"
        super().__init__(**kwargs)

    # Convert input_matrix into nested lists
    def matrix_builder(self, values_list):
        Mvalues_list = []
        temp_list = []
        order = int(self.root.ids.input_matrix.order)

        for i in range(order):
            for k in range(order):
                temp_list.append(values_list[order * i + k])
            Mvalues_list.append(list(temp_list))
            temp_list.clear()

        return Mvalues_list

    # ////// Receive values of matrix units provided in grid layout
    def calculate(self):

        # // Receives all text boxes of Matrix Grid
        children_list = self.root.ids.input_matrix.children
        if not children_list:  # // Checks that calculation not done on empty set of values
            return "---"
        values_list = []  # // List of all valid values user entered
        error_list = []
        for child in children_list:  # // Checks and Fetches all units of matrix one-by-one
            error = Validator().chk_value(child.text)

            if error and error not in error_list:
                error_list.append(error)
            elif not error:
                values_list.append(Fraction(child.text).limit_denominator(999))  # Value converted to fraction
        else:  # After checking all values for validity
            if len(error_list) != 0:  # If error present
                if len(error_list) > 4:
                    error_list.insert(3, '. . .')  # Add 3 dots if more than 4 errors
                error_list = error_list[0:4]  # Display max. 4 errors at a time
                error_string = '\n'.join(error_list)
                self.root.ids.display_box.text = error_string
                return "---"
            else:  # If all values are complete and error free
                self.root.ids.display_box.text = ''  # Removes error message when all values verified

        # // Covert Linear List to Matrix-type Nested List
        values_list.reverse()
        matrix_list = self.matrix_builder(values_list)

        # // Passes the matrix to calculate Determinant
        answer = Calculator().determinant(matrix_list)

        # // Sets the answer to display_box
        self.root.ids.display_box.text = "[b]Determinant:[/b]\n           [size=25sp][anchor='right']{answer}[/size]".format(answer=str(answer))

    # //// Sets the root of our window
    def build(self):
        if platform == "android":
            Window.softinput_mode = 'below_target'  # // Added to fix text-box hidden behind keyboard
            white_status_bar()
        else:
            Window.size = (450, 750)  # // Default size for desktop

        return MainWindow()


# Root layout of our app
class MainWindow(BoxLayout):
    pass


# ////// Class dedicated to calculating determinant of matrix
class Calculator:
    def determinant(self, A, total=0):
        # Section 1: store indices in list for row referencing

        indices = list(range(len(A)))

        # Section 2: when at 2x2 sub-matrices recursive calls end
        if len(A) == 2 and len(A[0]) == 2:
            val = A[0][0] * A[1][1] - A[1][0] * A[0][1]
            return val

        # Section 3: define sub-matrix for focus column and
        #      call this function
        for fc in indices:  # A) for each focus column, ...
            # find the sub-matrix ...
            As = list(A)  # B) make a copy, and ...
            As = As[1:]  # ... C) remove the first row
            height = len(As)  # D)

            for i in range(height):
                # E) for each remaining row of submatrix ...
                #     remove the focus column elements
                As[i] = As[i][0:fc] + As[i][fc + 1:]

            sign = (-1) ** (fc % 2)  # F)
            # G) pass sub-matrix recursively
            sub_det = Calculator().determinant(As)
            # H) total all returns from recursion
            total += sign * A[0][fc] * sub_det

        return total


# *****************************************************************************
# ////// Class dedicated to verify user inputs
class Validator:

    def chk_value(self, value):
        value = re.sub(r"\s", "", value)  # // Removes all types of whitespaces
        error = None

        master_pattern = re.compile(r"^((\+|\-)?\d{1,3}(([\.]\d{1,2})|([\/]\d{1,3}))?){1}$")

        # // Checks for standard pattern
        # // If false, then do some pre-tests to find exact problem
        if not re.match(master_pattern, value):
            if value == '':
                error = "! Any part of matrix can't be EMPTY."
            elif re.search(r"[^\+\-\.\/0-9]", value):
                error = "! Invalid characters in one/more values."
            elif len(re.findall(r"[\/]", value)) > 1:
                error = "! Multiple \'/\' in single value not allowed."
            elif re.search(r"[\/](\+|\-)", value):
                error = "! +/- can be in Numerator, NOT in Denominator."
            elif re.match(r"^((\+|\-)?\d{1,3}([\.]\d)?[\/](\+|\-)?\d{1,3}([\.]\d)?)$", value):
                error = "! Decimal and Fraction can't be together."
            elif re.search(r"\d{4,}", value):
                error = "! Max. 3 digits allowed for numerical part."
            else:
                error = "! Improper structure of entered value/s."

        # // Returns "None" for no errors
        # // Otherwise specified error statement
        return error


# /// Driver needed to self start the function ---- VROOM! VROOM!
if __name__ == "__main__":
    MatrixCalculator().run()
