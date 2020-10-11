# All the import statements needed in current version or upcoming version
import kivy
from kivy.metrics import sp
from kivy.properties import StringProperty

kivy.require('1.9.1')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivy.config import Config
from kivy.core.window import Window
import re
from fractions import Fraction

# // Search for resources in project root file (optional)
Config.write()
kivy.resources.resource_add_path("./")

# // Added to fix text-box hidden behind keyboard
Window.softinput_mode = 'below_target'


class MatrixValue(TextInput):
    def __init__(self, **kwargs):
        super(MatrixValue, self).__init__(**kwargs)
        self.multiline = False
        self.input_type = 'number'
        self.font_size = sp(25)
        self.font_family = 'bold'
        self.background_color = [0, 0.6, 0.3, 0.5]
        self.foreground_color = [1, 1, 0.8, 1]


# Development of grid layout that contains all the units of matrix
class MatrixGrid(GridLayout, BoxLayout):
    order = StringProperty('')

    # Function to make determinant as per the provided order
    def build_matrix(self, *args):
        error = Validator.chk_order(self.order)
        if error:
            self.parent.ids.error_box.text = error
            return
        else:
            self.parent.ids.error_box.text = ''

        order = int(self.order)

        self.clear_widgets()
        self.cols = order
        self.rows = order

        for i in range(1, order + 1):
            for k in range(1, order + 1):
                set_id = 'a' + str(i) + str(k)
                text_input = MatrixValue(id=set_id)
                self.add_widget(text_input)

    def on_order(self, *args):
        self.build_matrix(self)


### Our main App
### All the initiations, exchanges and processes done here
class matrixCalculator(MDApp):
    def __init__(self, **kwargs):
        self.title = "Matrix Calculator"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Gray"
        super().__init__(**kwargs)

    # Convert list of matrix values into rows and column type matrix
    def matrix_builder(self, values_list):
        Mvalues_list = []
        temp_list = []
        order = int(self.root.ids.order_input.text)

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
        for child in children_list: # // Checks and Fetches all units of matrix one-by-one
            error = Validator.chk_value(child.text)
            if error:
                self.root.ids.error_box.text = error # // Prints Error message
                return "----"
            else:
                values_list.append(Fraction(child.text).limit_denominator(999)) # Value converted to fraction
        else:
            self.root.ids.error_box.text = '' # // Removes error message when all values checked

        # // Covert Linear List to Matrix-type Nested List
        values_list.reverse()
        matrix_list = self.matrix_builder(values_list)

        # // Passes the matrix to calculate Determinant
        answer = Calculator.determinant(matrix_list)

        # // Sets the answer to show_answer label
        self.root.ids.show_answer.text = str(answer)

    # //// Sets the root of our window
    def build(self):
        return MainWindow()


# Root layout of our app
class MainWindow(BoxLayout):
    pass


# ////// Class dedicated to calculating determinant of matrix
class Calculator:
    def determinant(A, total=0):
        # Section 1: store indices in list for row referencing

        indices = list(range(len(A)))

        # Section 2: when at 2x2 submatrices recursive calls end
        if len(A) == 2 and len(A[0]) == 2:
            val = A[0][0] * A[1][1] - A[1][0] * A[0][1]
            return val

        # Section 3: define submatrix for focus column and 
        #      call this function
        for fc in indices:  # A) for each focus column, ...
            # find the submatrix ...
            As = list(A)  # B) make a copy, and ...
            As = As[1:]  # ... C) remove the first row
            height = len(As)  # D)

            for i in range(height):
                # E) for each remaining row of submatrix ...
                #     remove the focus column elements
                As[i] = As[i][0:fc] + As[i][fc + 1:]

            sign = (-1) ** (fc % 2)  # F)
            # G) pass submatrix recursively
            sub_det = Calculator.determinant(As)
            # H) total all returns from recursion
            total += sign * A[0][fc] * sub_det

        return total


# *****************************************************************************
# *****************************************************************************
# *****************************************************************************
# ////// Class dedicated to verify user inputs
class Validator:

    def chk_order(order):
        error = None
        order = order.strip()

        try:
            # // Raises Exception if any of below to conditions are not satisfied
            order = int(order)
            if order == '':
                raise Exception
            elif not (0 < order < 5):
                raise Exception
        except:
            error = "Order must be single digit in range 1 to 4."

        # // Returns "None" for no errors
        # // Otherwise specified error statement
        return error

    def chk_value(value):
        value = re.sub(r"\s", "", value)  # // Removes all types of whitespaces
        error = None

        master_pattern = re.compile(r"^((\+|\-)?\d{1,3}(([\.]\d{1,2})|([\/]\d{1,3}))?){1}$")

        # // Checks for standard pattern
        # // If false, then do some pre-tests to find exact problem
        if not re.match(master_pattern, value):
            if value == '':
                error = "Any part of matrix can't be left EMPTY."
            elif re.search(r"[^\+\-\.\/0-9]", value):
                error = "Invalid characters in one/more values."
            elif len(re.findall(r"[\/]", value)) > 1:
                error = "More than one \'/\' in single value not allowed."
            elif re.search(r"[\/](\+|\-)", value):
                error = "+/-  can only be in Numerator, NOT in Denominator."
            elif re.match(r"^((\+|\-)?\d{1,3}([\.]\d)?[\/](\+|\-)?\d{1,3}([\.]\d)?)$", value):
                error = "Both decimal and fraction can't be in a single value."
            elif re.search(r"\d{4,}", value):
                error = "Any Numerical part can't hold more than 3 digits."
            else:
                error = "Improper structure of entered value/s."

        # // Returns "None" for no errors
        # // Otherwise specified error statement
        return error


### Driver needed to self start the function ---- VROOM! VROOM!
if __name__ == "__main__":
    matrixCalculator().run()
