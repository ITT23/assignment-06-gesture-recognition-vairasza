class Font:
  COLOUR = (20,20,20,255)
  NAME = "Verdana"
  TEXT_SIZE = 15

class Color:
  BACKGROUND = (255,255,255,255)
  RECTS = (26, 159, 242, 255)
  RECTS_CORRECT = (0, 255, 0, 255)
  RECTS_WRONG = (255, 0, 0, 255)
  RECTS_HINT = (0, 3, 109, 255)

class Rects:
  NUM_X = 6
  NUM_Y = 3
  GAP = 10
  WIDTH = 200
  OFFSET = 7

class Gestures:
  MEMORIES = ["circle", "rectangle", "triangle"]
  EXIT = "x"
  RELOAD = "check"

class App:
  NAME = "Gesture Memory"
  WIDTH = 1280
  HEIGHT = 720
  CIRCLE_COLOUR = (255,0,0,255)
  CIRCLE_RADIUS = 5
  CIRCLE_COLOUR_START = (0,0,255,255)
  CIRCLE_RADIUS_START = 8
  SAMPLE_POINTS = 50

  TOO_FEW_POINTS = "Too few points drawn."

  FLASH_TIME = 2
  FLASH_TIME_GAP = 0.5

  END_OF_SEQUENCE_WAIT = 1

  GESTURE_SHOW_TIME = 0.2

  RECOGNISE_TEXT_X = 20
  RECOGNISE_TEXT_Y = 20
  STATE_TEXT_X = 20
  STATE_TEXT_Y = HEIGHT - 30

  START_GAME_TEXT = "STATE: SHOWING SEQUENCE"
  AWAIT_GAME_TEXT = "STATE: AWAITING YOUR GESTURE SEQUENCE"
  OVER_GAME_TEXT = "Game over! Sequence was incorrect! Draw X to end the game or CHECK to play a new game."
  WON_GAME_TEXT = "You managed to correctly guess the whole sequence. Congratulations!"