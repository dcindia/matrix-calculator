# All the import statements needed in current version or upcoming version
import kivy
from kivy.properties import ListProperty, OptionProperty
import os
import sys
from kivy.resources import resource_add_path
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from uixwidgets import MatrixValue
from kivy.utils import platform
from kivymd.app import MDApp
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
    from android.runnable import run_on_ui_thread  # type: ignore

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


# Development of grid layout that contains all the units of matrix
class MatrixGrid(GridLayout, BoxLayout):
    order = ListProperty([0, 0])

    # Function to make Matrix view as per the provided order
    def on_order(self, *args):

        try:
            MDApp.get_running_app().root.ids.display_box.text = ''
        except Exception:
            print("display_box still not created.")
        self.clear_widgets()
        self.rows = int(self.order[0])
        self.cols = int(self.order[1])

        for i in range(1, self.order[0] + 1):
            for k in range(1, self.order[1] + 1):
                set_id = 'a' + str(i) + str(k)
                text_input = MatrixValue()
                text_input.id = set_id
                self.add_widget(text_input)


# // Our main App
# // All the initiations, exchanges and processes done here
class MatrixCalculator(MDApp):
    operation_mode = OptionProperty('Determinant', options=['Determinant', 'Rank'])
    operation_type = OptionProperty('single', options=['single', 'double'])

    def __init__(self, **kwargs):
        self.title = "Matrix Calculator"
        self.theme_cls.theme_style = "Light"
        super().__init__(**kwargs)

    def set_operation(self, operation_name):
        self.operation_mode = operation_name

    # Convert input_matrix into nested lists
    def make_matrix(self):
        # // Receives all text boxes of Matrix Grid
        children_list = self.root.ids.input_matrix.children
        if not children_list:  # // Checks that calculation not done on empty set of values
            return "---"
        values_list = []  # // List of all valid values user entered
        error_list = []

        for child in children_list:  # // Checks and Fetches all units of matrix one-by-one
            error = Validator().chk_value(child.text, self.root.ids.input_matrix.order)

            if error and (error not in error_list):
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
        Mvalues_list = []
        temp_list = []
        order = self.root.ids.input_matrix.order

        for i in range(order[0]):
            for k in range(order[1]):
                temp_list.append(values_list[order[1] * i + k])
            Mvalues_list.append(list(temp_list))
            temp_list.clear()

        return Mvalues_list

    # ////// Receive values of matrix units provided in grid layout
    def calculate(self):
        matrix_list = self.make_matrix()
        if matrix_list == "---":
            return

        answer_string = ""
        WHITE_SPACE = "       "

        if self.operation_mode == "Determinant":
            determinant = Calculator().determinant(matrix_list)
            answer_string += f"Determinant:{WHITE_SPACE}[anchor='right']{determinant}"

        elif self.operation_mode == "Rank":
            rank = Calculator().rank_of_matrix(matrix_list)
            answer_string += f"Rank:{WHITE_SPACE}{rank}"

        else:
            answer_string += "Choose operation & re-calculate"

        # // Sets the answer to display_box
        self.root.ids.display_box.text = f"[size=25sp]{answer_string}[/size]"

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

    def minor_matrix(self, A, order):
        minors = []
        for i in range(len(A) - order + 1):
            partial_minor = A[i: i + order]
            for k in range(len(A[1]) - order + 1):
                minor = [B[k: k + order] for B in partial_minor]
                minors.append(minor)
        return minors

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

    def rank_of_matrix(self, A):
        max_rank = min(len(A), len(A[1]))
        print("**** Rank detection started ****")
        for k in reversed(range(1, max_rank + 1)):
            print("on order:", k)
            for f in self.minor_matrix(A, k):
                print("Checking for", f)
                det = self.determinant(f)
                print("Got Determinant:", det)
                if det != 0:
                    print("!! Accepted Rank:", k)
                    return k
        else:
            return 1


# *****************************************************************************
# ////// Class dedicated to verify user inputs
class Validator:

    def chk_value(self, value, order):
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

    def is_square_matrix(self, A):
        rows = len(A)
        for k in A:
            if len(k) != rows:
                return False
        else:
            return True


# /// Driver needed to self start the app ---- VROOM! VROOM!
if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MatrixCalculator().run()
