# gesture input program for first task
import time

from pyglet import app, window
from pyglet.shapes import Circle
from pyglet.text import Label
from pyglet.window import key

from recognizer import Point, Recogniser

class Font:
  COLOUR = (255,255,255,255)
  DETECTED_GESTURE = "Freely draw strokes on the canvas. Loaded templates: triangle, x, rectangle, cirlce and check."
  NAME = "Verdana"
  TEXT_X = 50
  TEXT_Y = 50
  TEXT_SIZE = 15

class Application:
  FPS = 1 / 60
  WIDTH = 1280
  HEIGTH = 720
  NAME = "Gesture Recogniser"

  CIRCLE_COLOUR = (255,0,0,255)
  CIRCLE_RADIUS = 5
  CIRCLE_COLOUR_START = (0,0,255,255)
  CIRCLE_RADIUS_START = 8

  def __init__(self) -> None:
    self.window = window.Window(self.WIDTH, self.HEIGTH, caption=self.NAME)
    self.on_draw = self.window.event(self.on_draw)
    self.on_key_press = self.window.event(self.on_key_press)

    self.on_mouse_drag = self.window.event(self.on_mouse_drag)
    self.on_mouse_release = self.window.event(self.on_mouse_release)
    self.on_mouse_press = self.window.event(self.on_mouse_press)

    self.recogniser = Recogniser()

    self.shapes: list[Circle] = []
    self.points: list[Point] = []

    self.label = Label(text=Font.DETECTED_GESTURE, font_name=Font.NAME, font_size=Font.TEXT_SIZE, bold=True, color=Font.COLOUR, x=Font.TEXT_X, y=Font.TEXT_Y)

  def run(self) -> None:
    app.run()        

  def on_draw(self) -> None:
    self.window.clear()

    for point in self.shapes:
      point.draw()
    self.label.draw()

    time.sleep(self.FPS)

  def on_mouse_drag(self, x: int, y: int, *_) -> None:
    #draws the first circle in blue and larger so that the starting points is recognisable
    if len(self.shapes) == 0:
      shape = Circle(x=x, y=y, radius=self.CIRCLE_RADIUS_START, color=self.CIRCLE_COLOUR_START)
    
    else:
      shape = Circle(x=x, y=y, radius=self.CIRCLE_RADIUS, color=self.CIRCLE_COLOUR)

    self.shapes.append(shape)
    self.points.append(Point(x,y))

  def on_mouse_release(self, *_) -> None:
    t1 = time.time()
    result = self.recogniser.recognise(self.points)

    #if points are too few or points are all on the same axis (leads to division by zero), returned template is none
    if result[0] == None:
      self.label.text = "Too few points drawn."
      return 

    gesture_name = result[0].name
    accuracy = format(result[1], ".2f")
    t_delta = round((time.time() - t1) * 1000)
    
    self.label.text = f"Result: {gesture_name} ({accuracy}) in {t_delta}ms."
    
  def on_mouse_press(self, *_) -> None:
    self.shapes = []
    self.points = []

  def on_key_press(self, symbol: int, _) -> None:
    if symbol == key.ESCAPE:
      app.exit()

if __name__ == "__main__":
  application = Application()
  application.run()