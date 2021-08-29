# All the import statements needed in current version or upcoming version
import itertools
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
    order = ListProperty([3, 3])

    # Function to make Matrix view as per the provided order
    def on_order(self, *args):

        app.error_list = []

        self.clear_widgets()
        self.rows = int(self.order[0])
        self.cols = int(self.order[1])

        for i in range(1, self.order[0] + 1):
            for k in range(1, self.order[1] + 1):
                text_input = MatrixValue()
                self.add_widget(text_input)

    def show_matrix(self, matrix):
        self.order = [len(matrix), len(matrix[0])]
        unpacked_matrix = list(itertools.chain(*matrix))
        unpacked_matrix.reverse()

        for k in range(0, len(unpacked_matrix)):
            self.children[k].readonly = True
            self.children[k].text = str(unpacked_matrix[k])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_order()


# // Our main App
# // All the initiations, exchanges and processes done here
class MatrixCalculator(MDApp):

    # Config_format === Operation_Type: (Input_type, Order_type, Output_type)
    operation_config = {'Determinant': ('single', 'square', 'number'),
                        'Rank': ('single', 'any', 'number'),
                        'Addition': ('double', 'same', 'matrix'),
                        'Product': ('double', 'chain', 'matrix'),
                        'Inverse': ('single', 'square', 'matrix')}
    operation_mode = OptionProperty('Determinant', options=operation_config.keys())
    error_list = ListProperty([])
    operation_type = OptionProperty('single', options=['single', 'double'])

    def __init__(self, **kwargs):
        self.title = "Matrix Calculator"
        self.theme_cls.theme_style = "Light"
        global app
        app = self
        super().__init__(**kwargs)

    def on_operation_mode(self, *args):
        self.root.ids.display_box.text = ""

    def on_error_list(self, obj, value):
        temp = list(value)
        temp = list(set(self.error_list))  # Removes same error multiple times
        temp = list(filter(None, temp))  # Removes Empty(None) values if any
        self.error_list = list(temp)

        length = len(temp)
        if length == 0:
            error_string = ""
        elif length < 4:
            error_string = '\n'.join(self.error_list[:4])
        else:
            error_string = '\n'.join(self.error_list[:3]) + "\n ..."

        self.root.ids.display_box.text = error_string

    # Convert input_matrix into nested lists
    def make_matrix(self, matrix):

        # // Receives all text boxes of Matrix Grid
        children_list = matrix.children
        if not children_list:  # // Checks that calculation not done on empty set of values
            return "---"

        error_observed = False
        self.error_list = []

        for child in children_list:  # // Checks and Fetches all units of matrix one-by-one
            error = Validator().chk_value(child.text)

            if error:
                error_observed = True
                self.error_list.append(error)

        if error_observed:
            return "---"
        else:
            self.error_list = []
            values_list = [Fraction(child.text).limit_denominator(999) for child in children_list]

        # // Covert Linear List to Matrix-type Nested List
        values_list.reverse()
        Mvalues_list = []
        temp_list = []
        order = matrix.order

        for i in range(order[0]):
            for k in range(order[1]):
                temp_list.append(values_list[order[1] * i + k])
            Mvalues_list.append(list(temp_list))
            temp_list.clear()

        return Mvalues_list

    # ////// Receive values of matrix units provided in grid layout
    def calculate(self):

        order_type = self.operation_config[self.operation_mode][1]
        improper_order = Validator().chk_order([self.root.ids.input_matrix_1.order, self.root.ids.input_matrix_2.order], order_type)
        if improper_order:
            return

        matrices_list = [self.make_matrix(self.root.ids.input_matrix_1)]
        if self.operation_config[self.operation_mode][0] == 'double':
            matrices_list.append(self.make_matrix(self.root.ids.input_matrix_2))

        if "---" in matrices_list:
            return

        answer_string = ""
        WHITE_SPACE = "     "

        if self.operation_mode == "Determinant":

            determinant = Calculator().determinant(matrices_list[0])
            answer_string += f"Determinant:{WHITE_SPACE}[anchor='right']{determinant}"

        elif self.operation_mode == "Rank":
            rank = Calculator().rank_of_matrix(matrices_list[0])
            answer_string += f"Rank:{WHITE_SPACE}{rank}"

        elif self.operation_mode == "Addition":
            sum = Calculator().add(matrices_list[0], matrices_list[1])
            answer_string += f"Sum:{WHITE_SPACE}"
            self.root.ids.output_matrix.show_matrix(sum)
            self.root.ids.ans_button.trigger_action()

        elif self.operation_mode == "Product":
            product = Calculator().product(matrices_list[0], matrices_list[1])
            answer_string += f"Product:{WHITE_SPACE}"
            self.root.ids.output_matrix.show_matrix(product)
            self.root.ids.ans_button.trigger_action()

        elif self.operation_mode == "Inverse":
            determinant = Calculator().determinant(matrices_list[0])
            if determinant == 0:
                self.root.ids.display_box.text = ""
                answer_string += "[size=19sp]Inverse not possible for matrix\nwhose determinant is 0.[/size]"
            else:
                inverse = Calculator().inverse(matrices_list[0])
                answer_string += f"Inverse:{WHITE_SPACE}"
                self.root.ids.output_matrix.show_matrix(inverse)
                self.root.ids.ans_button.trigger_action()

        else:
            answer_string += "Choose operation & re-calculate"

        # // Sets the answer to display_box
        self.root.ids.display_box.text = f"[size=29sp]{answer_string}[/size]"

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


class Calculator:

    def sub_matrix(self, A, order):
        """Extracts mini matrices from single Big matrix

        Args:
            A (List): Big matrix
            order (int): Order of smaller matrices needed

        Returns:
            List: List of mini matrices
        """
        minors = []
        for i in range(len(A) - order + 1):
            partial_minor = A[i: i + order]
            for k in range(len(A[1]) - order + 1):
                minor = [B[k: k + order] for B in partial_minor]
                minors.append(minor)
        return minors

    def transpose(self, A):
        transposed_matrix = [[k[t] for k in A] for t in range(len(A[0]))]
        return transposed_matrix

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

    def inverse(self, A):
        A_copy = list(A)
        det_A = self.determinant(A)
        inversed_matrix = []
        for i in range(len(A)):
            A_copy.pop(i)
            inversed_matrix.append([])
            for j in range(len(A[1])):
                minor_matrix = [k[:j] + k[j + 1:] for k in A_copy]
                cofactor = ((-1) ** (i + j)) * self.determinant(minor_matrix) / det_A
                inversed_matrix[i].append(cofactor)
                print(f"Cofactor = {cofactor} for {minor_matrix}")
            else:
                A_copy = list(A)
        else:
            inversed_matrix = self.transpose(inversed_matrix)

        return inversed_matrix

    def rank_of_matrix(self, A):
        max_rank = min(len(A), len(A[1]))
        print("**** Rank detection started ****")
        for k in reversed(range(1, max_rank + 1)):
            print("on order:", k)
            for f in self.sub_matrix(A, k):
                print("Checking for", f)
                det = self.determinant(f)
                print("Got Determinant:", det)
                if det != 0:
                    print("!! Accepted Rank:", k)
                    return k
        else:
            return 1

    def add(self, A, B):
        summed_matrix = [list(zip(m, n)) for m, n in zip(A, B)]
        for j in range(0, len(summed_matrix)):
            for k in range(0, len(summed_matrix[j])):
                pair = summed_matrix[j][k]
                summed_matrix[j][k] = pair[0] + pair[1]
        print(summed_matrix)
        return summed_matrix

    def product(self, A, B):
        group_by_column = [[k[t] for k in B] for t in range(len(B[0]))]
        print("Grouped by column =", group_by_column)
        product_matrix = []

        for j in A:
            row_matrix = []
            print("=============")

            for k in group_by_column:
                print("=============")
                print(j, '*', k)
                term = [m * n for m, n in zip(j, k)]
                row_matrix.append(sum(term))
                print("Answer =", sum(term))

            else:
                product_matrix.append(row_matrix)

        print("******************************")
        print("Final Product Matrix =", product_matrix)
        return product_matrix


"""
    B = [[3, 4, 5, 9], [1, -4, 5, 2], [-2, 8, 4, 4]]
    A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    product(A, B)
"""
"""
    A = [[Fraction(1), Fraction(2), Fraction(3), Fraction(-2)],
        [Fraction(4), Fraction(1, 3), Fraction(5), Fraction(6)],
        [Fraction(7), Fraction(9), Fraction(-3, 7), Fraction(8)],
        [Fraction(7), Fraction(3), Fraction(-1), Fraction(8, 3)]]
    inverse(A)
"""


class Validator:
    """Class dedicated to verify user inputs
    """

    def chk_value(self, value):
        """Checks for standard pattern. If False, then do some pre-tests to find exact problem.

        Args:
            value (Fraction): Fractional value entered in matrix

        Returns:
            String: Error statement if error found, otherwise None
        """
        value = re.sub(r"\s", "", value)  # // Removes all types of whitespaces
        error = None

        master_pattern = re.compile(r"^((\+|\-)?\d{1,3}(([\.]\d{1,2})|([\/]\d{1,3}))?){1}$")

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

        return error

    def chk_order(self, orders, order_type):
        error = ""

        if order_type == 'square':
            if orders[0][0] != orders[0][1]:
                error = "! Square matrix required for " + app.operation_mode
        elif order_type == 'same':
            if orders[0] != orders[1]:
                error = "! Order of both matrices should be same."
        elif order_type == 'chain':
            if orders[0][1] != orders[1][0]:
                error = "! Columns of M1 should equals to rows of M2"

        if error:
            app.error_list = [error]

        return error


# /// Driver needed to self start the app ---- VROOM! VROOM!
if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MatrixCalculator().run()
