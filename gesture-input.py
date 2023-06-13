# gesture input program for first task
import time

from pyglet import app, window
from pyglet.window import key
from pyglet.text import Label
from pyglet.shapes import Circle

from recognizer import Point, Recogniser

class Font:
  NAME = "Verdana"
  XLARGE = 20
  COLOUR = (255,255,255,255)
  DETECTED_GESTURE = ""
  TEXT_X = 50
  TEXT_Y = 50

class Application:
  WIDTH = 1280
  HEIGTH = 720
  NAME = "Gesture Recogniser"
  FPS = 1 / 60

  CIRCLE_COLOUR = (255,0,0,255)
  CIRCLE_RADIUS = 5

  def __init__(self) -> None:
    self.window = window.Window(self.WIDTH, self.HEIGTH, caption=self.NAME)
    self.on_draw = self.window.event(self.on_draw)
    self.on_key_press = self.window.event(self.on_key_press)

    self.on_mouse_drag = self.window.event(self.on_mouse_drag)
    self.on_mouse_release = self.window.event(self.on_mouse_release)
    self.on_mouse_press = self.window.event(self.on_mouse_press)

    self.recogniser = Recogniser()

    self.circles: list[Circle] = []
    self.points: list[Point] = []

    self.label = Label(text=Font.DETECTED_GESTURE, font_name=Font.NAME, font_size=Font.XLARGE, bold=True, color=Font.COLOUR, x=Font.TEXT_X, y=Font.TEXT_Y)

  def run(self) -> None:
    app.run()        

  def on_draw(self) -> None:
    self.window.clear()

    for point in self.circles:
      point.draw()
    self.label.draw()

    time.sleep(self.FPS)

  def on_mouse_drag(self, x, y, *_):
    circle = Circle(x=x, y=y, radius=self.CIRCLE_RADIUS, color=self.CIRCLE_COLOUR)
    self.circles.append(circle)
    self.points.append(Point(x,y))

  def on_mouse_release(self, *_):
    if len(self.points) > 1:
      t1 = time.time()
      result = self.recogniser.recognise(self.points)
      t_delta = round((time.time() - t1) * 1000)
      
      self.label.text = f"Result: {result[0].name} ({result[1]}) in {t_delta}ms."

    else:
      self.label.text = f"Too few points drawn."
    
  def on_mouse_press(self, *_):
    self.circles = []
    self.points = []

  def on_key_press(self, symbol, _):
    if symbol == key.ESCAPE:
      app.exit()

if __name__ == "__main__":
  application = Application()
  application.run()