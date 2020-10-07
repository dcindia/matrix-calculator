#!/usr/bin/env python
# coding: utf-8

# In[]:

### All the import statements needed in current version or upcoming version
import math
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.theming import ThemeManager
from kivymd.uix.textfield import MDTextFieldRound
from kivy.uix.effectwidget import EffectWidget
# In[]:

### A Window to contain our app
### Might not be required in Android OS upcoming Version
Window.clearcolor = (1,1,1,1)
Window.size = (600,400)


# In[ ]:

### This is a kivy file
### Instead of seperate file, it is provided inside the code
### It contains all the rules and parameters to structure our layout
Builder.load_string('''
#: import EffectWidget kivy.uix.effectwidget

### This is raw custom layout needed later in structure
<matrixInput>:
    
### This is entry point of our layout structure  
<mainWindow>:
    orientation: "vertical"
    ### This contains whole Part of App Heading
    BoxLayout:
        height: self.minimum_height
        size_hint_y: None
        padding: [dp(100),dp(8)]
       
        ### Draws a white background behind app heading
        ### Although not compulsary
        canvas:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        ### draws a grey line below heading for material feel
        canvas.before:
            Color:
                rgba: 0, 0, 0, 0.3
            Rectangle:
                pos: (self.pos[0] + 0,self.pos[1] - 3)
                size: self.size
       
        ### Button to show our Heading , but doesn't react on clicking
        MDRoundFlatButton:
            size_hint_x: 1
            pos_hint: {'center_x': 0.5}
            md_bg_color: 0,0,0,0
            text: "\t\tMatrix   Calculator\t\t"
            text_color: 0,0,0,0.85
            font_size: 24
            font_name: 'ERASDEMI.TTF'
      
    ### Contains block below heading for matrix input management
    BoxLayout:
        size_hint_y: None
        height: self.minimum_height
        
        ### Instruct user to enter order
        Label:
            size: self.texture_size
            text_size: self.size
            padding: (60,25)
            font_size: 18
            font_name: 'ERASMD.TTF'
            text: "Enter order of Matrix :"
            color: 0,0,0,1
        
        ### Accepts matrix order from user
        MDTextFieldRound:
            height: dp(30)
            padding: 0, dp(25), 0, dp(10)
            icon_type: 'without'
            width: dp(80)
            
            normal_color: [0,0,0,0.1]
            foreground_color: [0,0,0,1]
            font_size: 18
            font_family: 'bold'
            
            id: order_input
            on_text_validate: app.get_input()
        
        ### This is just an adjustment to position above text field correctly
        Widget:
            size_hint_x: None
    MDSeparator:
        
    ### Block below order input mangement to handle matrix values and answer
    BoxLayout:
        
        ### Block to place matrix to get input
        BoxLayout:
                    
            padding: dp(50)
            size_hint_x: 0.5
            
            ### This is an adjustment to position widgets
            Widget:
                size_hint_x: 0
                width: dp(1)
            
            ### A grid layout defined at starting of layout
            ### Contains all blocks as unit position of matrix
            ### Defined completely in python file for advanced functionality
            matrixInput:
                id: input_matrix
                pos_hint: {'left': 0}
                size_hint_x: 1
                spacing: dp(5)
                
        ### Block to Show answer related uses           
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.5
            padding: dp(12)
            spacing: dp(16)
            
            ### Button to initiate the calculation of provided matrix
            MDRaisedButton:
                on_press: app.get_matrix()
                
                text: 'Calculate >>'
                font_name: 'Azonix.otf'
                font_size: 20
                text_color: 1,1,1,1
                
                elevation_normal: 5
                opposite_colors: True
                md_bg_color: 1, 0.38, 0.38, 1
                
                pos_hint: {'center_x': 0.5}
                size_hint_x: 1
            
            ### This is the place to show the calculated answer
            Label:
                id: show_answer
                        
                text: ' '
                font_name: 'Segment7Standard.otf'
                font_size: 70
                color: 0,0,0,1
            
            ### This is an adjustment to place widgets correctly
            Widget:
                size_hint_y: None
                height: 0
            
''')


# In[ ]:

    
### Class for starting point of our app
class mainWindow(BoxLayout):
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Gray'

### Development of grid layout that contains all the units of matrix  
class matrixInput(GridLayout):

    ### Function to make determinant as per the provided order    
    def build(self,order):
        
        self.clear_widgets()
        self.cols = order
        self.rows = order
        
        box_color = [0,0.6,0.3,0.7]
        text_color = [1,1,0.8,1]
        
        for i in range (1,order+1):
            for k in range (1,order+1):
                set_id = 'a' + str(i) + str(k)
                text_input = TextInput(id= set_id, multiline = False,input_type= 'number', font_size = 20,background_color = box_color,foreground_color = text_color)
                self.add_widget(text_input)

    ### Initiator required to create layout
    def __init__(self, **kwargs):
        super(matrixInput, self).__init__(**kwargs)
        self.build(0)


# In[ ]:

### Our main App 
### All the initiations, exchanges and processes done here
class matrixCalculator(App):
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Gray'
    
    ### Receive order from user
    def get_input(self):
        order =  int(self.root.ids.order_input.text)
        self.root.ids.input_matrix.build(order)
    ### Convert list of matrix values into rows and column type matrix    
    def matrix_builder(self,values_list): 
        Mvalues_list = []
        temp_list = []
        order = int(math.sqrt(len(values_list)))
        
        for i in range (order):
            for k in range (order):
                temp_list.append(values_list[(order)*i + k ])
            Mvalues_list.append(list(temp_list))
            temp_list.clear()
            
        return Mvalues_list
    
    
    ### Receive values of matrix units provided in grid layout   
    def get_matrix(self):
        
        ### Get List of values from matrix_input
        children_list = self.root.ids.input_matrix.children
        values_list = []
        for child in children_list:
            values_list.append(int(child.text))
        
        ### passing values to convert in matrix form
        values_list.reverse()
        matrix_list = self.matrix_builder(values_list)
        
        ### get determinant value from value dedicated class
        determinant = Determinant()
        answer = Determinant.determinantOfMatrix(matrix_list)
        
        ### Sets the answer to show_answer
        self.root.ids.show_answer.text = str(answer)
    
    ### Sets mainWindow as root of our window
    def build(self):
        return mainWindow()


# In[ ]:

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
        for fc in indices: # A) for each focus column, ...
            # find the submatrix ...
            As = list(A) # B) make a copy, and ...
            As = As[1:] # ... C) remove the first row
            height = len(As) # D) 
     
            for i in range(height): 
                # E) for each remaining row of submatrix ...
                #     remove the focus column elements
                As[i] = As[i][0:fc] + As[i][fc+1:] 
     
            sign = (-1) ** (fc % 2) # F) 
            # G) pass submatrix recursively
            sub_det = Determinant.determinantOfMatrix(As)
            # H) total all returns from recursion
            total += sign * A[0][fc] * sub_det 
     
        return total

### Driver needed to self start the function ---- VROOM! VROOM!
if __name__ == "__main__":
    matrixCalculator().run()
