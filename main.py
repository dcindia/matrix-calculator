# All the import statements needed in current version or upcoming version
import math
import kivy
from kivy.metrics import sp
from kivy.properties import NumericProperty, StringProperty, ObjectProperty

kivy.require('1.9.1')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivy.config import Config
from fractions import Fraction

Config.write()
kivy.resources.resource_add_path("./")


# Class for starting point of our app
class MainWindow(BoxLayout):
    pass


# Development of grid layout that contains all the units of matrix
class MatrixGrid(GridLayout, BoxLayout):
    order = StringProperty('')

    # Function to make determinant as per the provided order
    def build_matrix(self, *args):
        if self.order == '':
            self.order = '0'
        order = int(self.order)

        self.clear_widgets()
        self.cols = order
        self.rows = order

        box_color = [0, 0.6, 0.3, 0.5]
        text_color = [1, 1, 0.8, 1]

        for i in range(1, order + 1):
            for k in range(1, order + 1):
                set_id = 'a' + str(i) + str(k)
                text_input = TextInput(id=set_id, multiline=False, input_type='number', font_size=sp(25),
                                       background_color=box_color, foreground_color=text_color,
                                       font_family='bold')
                self.add_widget(text_input)

    def on_order(self, *args):
        self.build_matrix(self)
    ### Initiator required to create layout


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
                temp_list.append(values_list[(order) * i + k])
            Mvalues_list.append(list(temp_list))
            temp_list.clear()

        return Mvalues_list

    ### Receive values of matrix units provided in grid layout   
    def calculate(self):

        # ////// Get user-entered Matrix in List Form
        # ////// Also converts String input to Fraction object
        children_list = self.root.ids.input_matrix.children
        values_list = []
        for child in children_list:
            values_list.append(Fraction(child.text).limit_denominator(999))

        # ////// Covert Linear List to Matrix-type Nested List
        values_list.reverse()
        matrix_list = self.matrix_builder(values_list)

        # ////// Passes the matrix to calculate Determinant
        determinant = Determinant()
        answer = Determinant.determinantOfMatrix(matrix_list)

        ### Sets the answer to show_answer
        self.root.ids.show_answer.text = str(answer)

    ### Sets  as root of our window
    def build(self):
        return MainWindow()


#### Class dedicated to calculating determinant of matrix
class Determinant():
    def determinantOfMatrix(A, total=0):
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
            sub_det = Determinant.determinantOfMatrix(As)
            # H) total all returns from recursion
            total += sign * A[0][fc] * sub_det

        return total


### Driver needed to self start the function ---- VROOM! VROOM!
if __name__ == "__main__":
    matrixCalculator().run()
