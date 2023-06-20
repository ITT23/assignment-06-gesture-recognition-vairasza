# application for task 3
# gesture input program for first task
import time, random, os
from typing import Union

from pyglet import app, media, window
from pyglet.clock import schedule_once
from pyglet.shapes import Circle, Rectangle
from pyglet.text import Label

from game.Config import Color, Font, Rects, Gestures, App
from recognizer import Recogniser, Point, Template


class GameState:
  SHOW = 1
  INTER = 2
  AWAIT = 3
  END = 4
  WON = 5


class Card:

  def __init__(self, idx: int, x: int, y: int, width: float, height: float, color: tuple) -> None:
    self.idx = idx
    self.template_name = random.choice(Gestures.MEMORIES)

    self.result_indicator = Rectangle(x=x-Rects.OFFSET, y=y-Rects.OFFSET, width=width + (2 * Rects.OFFSET), height=height + (2 * Rects.OFFSET), color=Color.RECTS_CORRECT)
    self.background = Rectangle(x=x, y=y, width=width, height=height, color=color)
    self.label = Label(text=self.template_name, x=x, y=y, color=Font.COLOUR, font_name=Font.NAME, font_size=Font.TEXT_SIZE, bold=True)
    self._center_label(x, y)

    self.result_indicator.visible = False
    self.label.visible = False

  def _center_label(self, x: int, y: int) -> None:
    x = (Rects.WIDTH / 2 + x) - self.label.content_width / 2
    y = (Rects.WIDTH / 2 + y) - self.label.content_height / 2
    self.label.x = x
    self.label.y = y
  
  def collision_quantity(self, points: list[Point]) -> int:
    '''
      a gesture consists of many points... to check the box that the user intents to draw on, we return a value for each collision with a box and conclude that the box with the most collision is the intended box.
      requires a list of points that are not already resampled/scaled/turned etc.
    '''
    counter = 0

    for p in points:
      if p.x >= self.background.x and p.x <= self.background.x + self.background.width and p.y >= self.background.y and p.y <= self.background.y + self.background.height:
        counter += 1

    return counter   

  def hint(self, start_delay: int, stop_delay: int) -> None:
    self.result_indicator.color = Color.RECTS_HINT

    schedule_once(self.turn, start_delay)
    schedule_once(self.unturn, stop_delay)

  def correct(self) -> None:
    self.result_indicator.color = Color.RECTS_CORRECT
    self.turn()

  def wrong(self) -> None:
    self.result_indicator.color = Color.RECTS_WRONG
    self.turn()

  def turn(self, *_) -> None:
    self.label.visible = True
    self.result_indicator.visible = True

  def unturn(self, *_) -> None:
    self.label.visible = False
    self.result_indicator.visible = False

  def draw(self) -> None:
    self.result_indicator.draw()
    self.background.draw()
    self.label.draw()


class Menu:

  def __init__(self) -> None:
    self.recogniser_indicator = Label(text="", font_name=Font.NAME, font_size=Font.TEXT_SIZE, bold=True, color=Font.COLOUR, x=App.RECOGNISE_TEXT_X, y=App.RECOGNISE_TEXT_Y)
    self.state_indicator = Label(text="", font_name=Font.NAME, font_size=Font.TEXT_SIZE, bold=True, color=Font.COLOUR, x=App.STATE_TEXT_X, y=App.STATE_TEXT_Y)

  def too_few_points(self) -> None:
    self.recogniser_indicator.text = App.TOO_FEW_POINTS

  def recognition_result(self, result: Template, time: int) -> None:
    accuracy = format(result[1], ".2f")
    t_delta = round((time) * 1000)
    
    self.recogniser_indicator.text = f"Result: {result[0].name} ({accuracy}) in {t_delta}ms."

  def draw(self) -> None:
    self.recogniser_indicator.draw()
    self.state_indicator.draw()

  def start_game(self) -> None:
    self.state_indicator.text = App.START_GAME_TEXT

  def await_game(self) -> None:
    self.state_indicator.text = App.AWAIT_GAME_TEXT

  def game_over(self) -> None:
    self.state_indicator.text = App.OVER_GAME_TEXT

  def game_won(self) -> None:
    self.state_indicator.text = App.WON_GAME_TEXT


class Game():

  SCRIPT_DIR = os.path.dirname(__file__)

  def __init__(self, width: int, height: int, menu: Menu) -> None:
    self.menu = menu
    self.sound_file = media.load(os.path.join(self.SCRIPT_DIR, App.SOUNDFILE))
    self.audio_player = media.Player()
    self.cards: list[Card] = []
    self.sequence: list[int] = list(range(18))
    random.shuffle(self.sequence)

    self.sequence_index = 0 #this indicates how many cards are turned in a sequence
    self.player_index = 0 #this indicates the number of sequence items a player has correctly guessed
    self.state = GameState.SHOW
    self._draw_cards(width, height)

  def _draw_cards(self, width: int, height: int) -> None:
    padding_x = (width - (Rects.NUM_X * Rects.WIDTH + Rects.GAP * (Rects.NUM_X - 1))) / 2
    padding_y = (height - (Rects.NUM_Y * Rects.WIDTH + Rects.GAP * (Rects.NUM_Y - 1))) / 2

    for i in range(Rects.NUM_X):
      for j in range(Rects.NUM_Y):
        x = padding_x + i * Rects.GAP + i * Rects.WIDTH
        y = padding_y + j * Rects.GAP + j * Rects.WIDTH
        idx = i + j + i * (Rects.NUM_Y - 1)

        card = Card(idx=idx,x=x, y=y, width=Rects.WIDTH, height=Rects.WIDTH, color=Color.RECTS)
        
        self.cards.append(card)

  def _check_collision(self, points: list[Point]) -> Union[Card, None]:
    intented_card: Card = None
    current_quantity = 0

    for card in self.cards:
      quantity = card.collision_quantity(points)
      if quantity > current_quantity:
        current_quantity = quantity
        intented_card = card

    return intented_card

  def handle_gesture(self, points: list[Point], gesture_name: str) -> None:
    #returns true if game state is currently on show so that the user knows that the computer is still showing the current sequence and the player has to wait.
    if self.state is not GameState.AWAIT:
      return

    collided_card = self._check_collision(points)

    #if player reaches the end of the game because all cards are correctly guessed
    if collided_card.label.text == gesture_name and collided_card.idx == self.sequence[self.sequence_index] and self.sequence_index == self.player_index and len(self.sequence) - 1 == self.player_index:
      self.state = GameState.END #game won

    #if player reached the current sequence index
    elif collided_card.label.text == gesture_name and collided_card.idx == self.sequence[self.sequence_index] and self.sequence_index == self.player_index:
      collided_card.correct() #this can stay open until the end
      self.sequence_index += 1 #player advances and can input the next gesture
      
      schedule_once(self._change_state_to_show, App.END_OF_SEQUENCE_WAIT) #wait a second so that the player better understand that the last item in the sequence was correct

    #if player guess the current card in sequence
    elif collided_card.label.text == gesture_name and collided_card.idx == self.sequence[self.player_index]:
      collided_card.correct()
      self.player_index += 1

    else:
      correct_card = self.cards[self.sequence[self.player_index]]
      correct_card.correct()
      
      collided_card.wrong()

      self.state = GameState.END


  def _change_state_to_show(self, *_) -> None:
    self.state = GameState.SHOW

  def _change_state_to_await(self, *_) -> None:
    self.state = GameState.AWAIT
    self.audio_player.queue(self.sound_file)
    self.audio_player.play()

  def _turn_all_cards(self) -> None:
    for card in self.cards:
      card.unturn()

  def draw(self):
    for card in self.cards:
      card.draw()

    if self.state == GameState.SHOW:
      self.menu.start_game()

      self._turn_all_cards()

      last_delay = 0
      #shows the cards with their designated gesture in sequence defined with schedule_once function
      for i in range(self.sequence_index + 1):
        start_delay = i * App.FLASH_TIME + (i - 1) * App.FLASH_TIME_GAP
        stop_delay = start_delay + App.FLASH_TIME
        last_delay = stop_delay #mark for game state change so that drawn gestures are processed as player sequence

        self.cards[self.sequence[i]].hint(start_delay, stop_delay)
      
      schedule_once(self._change_state_to_await, last_delay)
      self.state = GameState.INTER
      self.player_index = 0
    
    elif self.state == GameState.AWAIT:
      self.menu.await_game()

    elif self.state == GameState.END:
      self.menu.game_over()

    elif self.state == GameState.WON:
      self.menu.game_won()


class Application:

  FPS = 1/60

  def __init__(self) -> None:
    self.window = window.Window(width=App.WIDTH, height=App.HEIGHT, caption=App.NAME)
    self.background = Rectangle(x=0, y=0, width=self.window.width, height=self.window.height, color=Color.BACKGROUND)
    self.on_draw = self.window.event(self.on_draw)

    self.on_mouse_drag = self.window.event(self.on_mouse_drag)
    self.on_mouse_release = self.window.event(self.on_mouse_release)
    self.on_mouse_press = self.window.event(self.on_mouse_press)

    self.recogniser = Recogniser()
    self.menu = Menu()

    self._init()
    
  def _init(self) -> None:
    self.game = Game(self.window.width, self.window.height, self.menu)
    self._clear_gesture()

  def _clear_gesture(self, *_) -> None:
    self.circles: list[Circle] = []
    self.points: list[Point] = []

  def run(self) -> None:
    app.run()        

  def on_draw(self) -> None:
    self.window.clear()
    self.background.draw()
    
    self.game.draw()
    for circle in self.circles:
      circle.draw()
    
    self.menu.draw()

    time.sleep(self.FPS)

  def on_mouse_drag(self, x: int, y: int, *_) -> None:
    if len(self.circles) == 0:
      circle = Circle(x=x, y=y, radius=App.CIRCLE_RADIUS_START, color=App.CIRCLE_COLOUR_START)
    
    else:
      circle = Circle(x=x, y=y, radius=App.CIRCLE_RADIUS, color=App.CIRCLE_COLOUR)

    self.circles.append(circle)
    self.points.append(Point(x,y))

  def on_mouse_release(self, *_) -> None:
    t1 = time.time()
    result = self.recogniser.recognise(self.points)
    t2 = time.time()

    if result[0] == None:
      self.menu.too_few_points()
      return

    gesture_name = result[0].name
    delay = t2 - t1

    self.menu.recognition_result(result, delay)

    if gesture_name in Gestures.MEMORIES:
      self.game.handle_gesture(self.points, gesture_name)

    elif gesture_name == Gestures.RELOAD:#reload the game by drawing a check gesture
      self._init()

    elif gesture_name == Gestures.EXIT:#exit the game by drawing a x gesture
      app.exit()

    schedule_once(self._clear_gesture, App.GESTURE_SHOW_TIME)
    
  def on_mouse_press(self, *_) -> None:
    self._clear_gesture()


if __name__ == "__main__":
  application = Application()
  application.run()