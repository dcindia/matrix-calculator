from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from math import sin, cos, pi

kv = '''
#<KvLang>
<RoundedBox>:
    canvas.before:
        Color:
            rgb: self.color
        Line:
            points: self.points
            width: self.line_width

<ToggleOperation@ToggleButton>:
    canvas.before:
        Color:
            rgba: utils.get_color_from_hex('#42B1FA') if self.state == 'normal' else utils.get_color_from_hex('#186DC9')
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(3.5),]

    background_normal: ''
    background_color: 0,0,0,0
    background_down: ''

    size_hint: None, None
    padding: dp(10), dp(5)
    size: self.texture_size

    allow_no_selection: False
    group: 'choose_operation'
    on_state: app.operation_mode = self.text

<ToggleMatrix@ToggleButton>:
    canvas.before:
        Color:
            rgba: utils.get_color_from_hex('#0099FF')
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(4), ]

    background_normal: ''
    background_color: 0,0,0,0

    font_name: "Roboto-Bold.ttf"
    font_size: sp(15)

    size_hint: None, 1
    width: self.height

    group: 'choose_matrix'
    allow_no_selection: False

    RoundedBox:
        opacity: 1 if self.parent.state == 'down' else 0
        center: self.parent.center
        size: self.parent.size
        line_width: dp(1.2)
        corners: [dp(4), dp(4), dp(4), dp(4)]
#</KvLang>
'''
Builder.load_string(kv)


class RoundedBox(Widget):
    color = ListProperty([0, 153, 255])
    corners = ListProperty([0, 0, 0, 0])
    line_width = NumericProperty(1)
    resolution = NumericProperty(100)
    points = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.compute_points, size=self.compute_points, corners=self.compute_points, resolution=self.compute_points, center=self.compute_points)

    def compute_points(self, *args):
        self.points = []

        a = - pi

        x = self.x + self.corners[0]
        y = self.y + self.corners[0]
        while a < - pi / 2.:
            a += pi / self.resolution
            self.points.extend([
                x + cos(a) * self.corners[0],
                y + sin(a) * self.corners[0]
            ])

        x = self.right - self.corners[1]
        y = self.y + self.corners[1]
        while a < 0:
            a += pi / self.resolution
            self.points.extend([
                x + cos(a) * self.corners[1],
                y + sin(a) * self.corners[1]
            ])

        x = self.right - self.corners[2]
        y = self.top - self.corners[2]
        while a < pi / 2.:
            a += pi / self.resolution
            self.points.extend([
                x + cos(a) * self.corners[2],
                y + sin(a) * self.corners[2]
            ])

        x = self.x + self.corners[3]
        y = self.top - self.corners[3]
        while a < pi:
            a += pi / self.resolution
            self.points.extend([
                x + cos(a) * self.corners[3],
                y + sin(a) * self.corners[3]
            ])

        self.points.extend(self.points[:2])


class MatrixValue(TextInput):
    def __init__(self, **kwargs):
        super(MatrixValue, self).__init__(**kwargs)
        self.background_normal = ''
        self.multiline = False
        self.write_tab = False
        self.padding_y = dp(self.width / 8)
        self.font_size = sp(20)
        self.background_color = [0, 0, 0, 0]

        self.cursor_color = (0, 0, 0, 0)
        self.fg_color = get_color_from_hex('#240E43')
        bg_color = get_color_from_hex('#13be8b')
        self.dummy_cursor_color = (0, 0, 0, 0)
        with self.canvas.before:
            Color(*bg_color)
            self.rounded_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(6), ])
            Color(*self.fg_color)
        self.bind(pos=self.update_roundedbg, size=self.update_roundedbg, focus=self.cursor_visibility)

    def add_cursor(self, cursor_color):
        with self.canvas.after:
            self.canvas.after.clear()
            Color(*cursor_color)
            self.dummy_cursor = Rectangle(pos=self.cursor_pos, size=(self.cursor_width * 2, -self.line_height))

        self.bind(cursor_pos=self.update_cursor_pos)

    def update_roundedbg(self, *args):
        self.rounded_bg.pos = self.pos
        self.rounded_bg.size = self.size

    def update_cursor_pos(self, *args):
        self.dummy_cursor.pos = self.cursor_pos

    def cursor_visibility(self, *args):
        self.add_cursor([1, 0, 0, 1] if self.focus else [0, 0, 0, 0])
