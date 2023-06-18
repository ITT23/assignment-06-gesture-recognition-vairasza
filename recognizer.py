# $1 gesture recognizer
#file is based on https://depts.washington.edu/acelab/proj/dollar/dollar.pdf
import math

class Point:
  def __init__(self, x: float, y: float) -> None:
    self.x = x
    self.y = y

class Config:
  SAMPLE_POINTS = 64
  SIZE = 250.0
  ORIGIN = Point(0,0)
  THETA_POS = 45.0
  THETA_NEG = -45.0
  THETA_DELTA = 2.0
  PHI = 0.5 * (-1.0 + math.sqrt(5.0))
  HALF_DIAGONAL = 0.5 * math.sqrt(SIZE * SIZE + SIZE * SIZE)
  REQUIRED_POINTS = 3

class Template:
  def __init__(self, index: int, name: str, points: list[Point]) -> None:
    self.index = index
    self.name = name
    self.points = points

def _distance(a: Point, b: Point) -> float:
  d_x = b.x - a.x
  d_y = b.y - a.y

  return math.sqrt(d_x * d_x + d_y * d_y)

def _resample(points: list[Point], n: int) -> list[Point]:
  I = _path_length(points) / (n - 1)
  D = 0.0

  new_points: list[Point] = []
  new_points.append(points[0])

  for (key, _) in enumerate(points):
    if key == 0:
      continue
    d = _distance(points[key - 1], points[key])

    if (D + d) >= I:
      q_x = points[key - 1].x + ((I - D) / d) * (points[key].x - points[key - 1].x)
      q_y = points[key - 1].y + ((I -D) / d) * (points[key].y - points[key - 1].y)
      
      new_point = Point(q_x, q_y)
      new_points.append(new_point)
      #need to insert the updated point into the initial list so that the next iteration can work with the updated point
      points.insert(key, new_point)

      D = 0.0

    else:
      D = D + d

  #https://depts.washington.edu/acelab/proj/dollar/dollar.js; addition to the pseudo code; sometimes the sample is one element too short
  if len(new_points) == n - 1:
    new_points.append(points[-1])
  
  return new_points

def _path_length(points: list[Point]) -> float:
  d = 0.0

  for i in range(1, len(points)):
    d = d + _distance(points[i - 1], points[i])

  return d

def _indicative_angle(points: list[Point]) -> float:
  c = _centroid(points)

  return math.atan2(c.y - points[0].y, c.x - points[0].x)


def _centroid(points: list[Point]) -> Point:
  l_x = [p.x for p in points]
  l_y = [p.y for p in points]

  return Point(sum(l_x) / len(points), sum(l_y) / len(points))

def _rotate_by(points: list[Point], theta: float) -> list[Point]:
  new_points: list[Point] = []
  c = _centroid(points=points) 
  sin = math.sin(theta)
  cos = math.cos(theta)

  for p in points:
    q_x = (p.x - c.x) * cos - (p.y - c.y) * sin + c.x
    q_y = (p.x - c.x) * sin + (p.y - c.y) * cos + c.y

    new_points.append(Point(q_x, q_y))
  
  return new_points

def _bounding_box(points: list[Point]) -> tuple[Point, Point]:
  l_x = [p.x for p in points]
  l_y = [p.y for p in points]

  min_x = min(l_x)
  max_x = max(l_x)
  min_y = min(l_y)
  max_y = max(l_y)
  
  return (Point(min_x, min_y), Point(max_x, max_y))

def _scale_to(points: list[Point], size: int) -> list[Point]:
  new_points: list[Point] = []
  b = _bounding_box(points=points)
  b_width = abs(b[1].x - b[0].x)
  b_height = abs(b[1].y - b[0].y)

  for p in points:
    q_x = p.x * (size / b_width)
    q_y = p.y * (size / b_height)

    new_points.append(Point(q_x, q_y))
  
  return new_points

def _translate_to(points: list[Point], origin: Point) -> list[Point]:
  new_points: list[Point] = []
  c = _centroid(points=points)

  for p in points:
    q_x = p.x + origin.x - c.x
    q_y = p.y + origin.y - c.y

    new_points.append(Point(q_x, q_y))

  return new_points

def _path_distance(points: list[Point], template: list[Point]) -> float:
  d = 0.0
  
  #https://stackoverflow.com/a/1663826/13620136
  for (p, t) in zip(points, template):
    d = d + _distance(p, t)

  return d / len(points)

def _distance_at_angle(points: list[Point], template: list[Point], theta: float) -> float:
  new_points = _rotate_by(points, theta)
  d = _path_distance(new_points, template)

  return d

def _distance_at_best_angle(points: list[Point], template: Template, phi: float, theta_neg: float, theta_pos: float, theta_delta: float) -> float:
  x_1 = phi * theta_neg + (1.0 - phi) * theta_pos
  f_1 = _distance_at_angle(points, template.points, x_1)

  x_2 = (1.0 - phi) * theta_neg + phi * theta_pos
  f_2 = _distance_at_angle(points, template.points, x_2)

  while abs(theta_pos - theta_neg) > theta_delta:
    if f_1 < f_2:
      theta_pos = x_2
      x_2 = x_1
      f_2 = f_1
      x_1 = phi * theta_neg + (1.0 - phi) * theta_pos
      f_1 = _distance_at_angle(points, template.points, x_1)

    else:
      theta_neg = x_1
      x_1 = x_2
      f_1 = f_2
      x_2 = (1.0 - phi) * theta_neg + phi * theta_pos
      f_2 = _distance_at_angle(points, template.points, x_2)

  return min(f_1, f_2)

def _convert_points(points: list[Point]) -> list[Point]:
    points = _resample(points, Config.SAMPLE_POINTS)
    rad = _indicative_angle(points)
    points = _rotate_by(points, -rad)
    points = _scale_to(points, Config.SIZE)
    points = _translate_to(points, Config.ORIGIN)

    return points

def _mirror_points(points: list[Point]) -> list[Point]:
  new_points = []
  for p in points:
    new_points.append(Point(-1 * p.x, p.y))

  return new_points

def _evaluate_list(points: list[Point]) -> bool:
  if len(points) <= Config.REQUIRED_POINTS:
    return False
  
  p_min, p_max = _bounding_box(points)

  if p_min.x == p_max.x or p_min.y == p_max.y:
    return False
  
  return True

predefined_gestures: dict[str, list[Point]] = {
  "triangle": [Point(137,139),Point(135,141),Point(133,144),Point(132,146),Point(130,149),Point(128,151),Point(126,155),Point(123,160),Point(120,166),Point(116,171),Point(112,177),Point(107,183),Point(102,188),Point(100,191),Point(95,195),Point(90,199),Point(86,203),Point(82,206),Point(80,209),Point(75,213),Point(73,213),Point(70,216),Point(67,219),Point(64,221),Point(61,223),Point(60,225),Point(62,226),Point(65,225),Point(67,226),Point(74,226),Point(77,227),Point(85,229),Point(91,230),Point(99,231),Point(108,232),Point(116,233),Point(125,233),Point(134,234),Point(145,233),Point(153,232),Point(160,233),Point(170,234),Point(177,235),Point(179,236),Point(186,237),Point(193,238),Point(198,239),Point(200,237),Point(202,239),Point(204,238),Point(206,234),Point(205,230),Point(202,222),Point(197,216),Point(192,207),Point(186,198),Point(179,189),Point(174,183),Point(170,178),Point(164,171),Point(161,168),Point(154,160),Point(148,155),Point(143,150),Point(138,148),Point(136,148)],
	
  "x": [Point(87,142),Point(89,145),Point(91,148),Point(93,151),Point(96,155),Point(98,157),Point(100,160),Point(102,162),Point(106,167),Point(108,169),Point(110,171),Point(115,177),Point(119,183),Point(123,189),Point(127,193),Point(129,196),Point(133,200),Point(137,206),Point(140,209),Point(143,212),Point(146,215),Point(151,220),Point(153,222),Point(155,223),Point(157,225),Point(158,223),Point(157,218),Point(155,211),Point(154,208),Point(152,200),Point(150,189),Point(148,179),Point(147,170),Point(147,158),Point(147,148),Point(147,141),Point(147,136),Point(144,135),Point(142,137),Point(140,139),Point(135,145),Point(131,152),Point(124,163),Point(116,177),Point(108,191),Point(100,206),Point(94,217),Point(91,222),Point(89,225),Point(87,226),Point(87,224)],

  "rectangle": [Point(78,149),Point(78,153),Point(78,157),Point(78,160),Point(79,162),Point(79,164),Point(79,167),Point(79,169),Point(79,173),Point(79,178),Point(79,183),Point(80,189),Point(80,193),Point(80,198),Point(80,202),Point(81,208),Point(81,210),Point(81,216),Point(82,222),Point(82,224),Point(82,227),Point(83,229),Point(83,231),Point(85,230),Point(88,232),Point(90,233),Point(92,232),Point(94,233),Point(99,232),Point(102,233),Point(106,233),Point(109,234),Point(117,235),Point(123,236),Point(126,236),Point(135,237),Point(142,238),Point(145,238),Point(152,238),Point(154,239),Point(165,238),Point(174,237),Point(179,236),Point(186,235),Point(191,235),Point(195,233),Point(197,233),Point(200,233),Point(201,235),Point(201,233),Point(199,231),Point(198,226),Point(198,220),Point(196,207),Point(195,195),Point(195,181),Point(195,173),Point(195,163),Point(194,155),Point(192,145),Point(192,143),Point(192,138),Point(191,135),Point(191,133),Point(191,130),Point(190,128),Point(188,129),Point(186,129),Point(181,132),Point(173,131),Point(162,131),Point(151,132),Point(149,132),Point(138,132),Point(136,132),Point(122,131),Point(120,131),Point(109,130),Point(107,130),Point(90,132),Point(81,133),Point(76,133)],

  "circle": [Point(127,141),Point(124,140),Point(120,139),Point(118,139),Point(116,139),Point(111,140),Point(109,141),Point(104,144),Point(100,147),Point(96,152),Point(93,157),Point(90,163),Point(87,169),Point(85,175),Point(83,181),Point(82,190),Point(82,195),Point(83,200),Point(84,205),Point(88,213),Point(91,216),Point(96,219),Point(103,222),Point(108,224),Point(111,224),Point(120,224),Point(133,223),Point(142,222),Point(152,218),Point(160,214),Point(167,210),Point(173,204),Point(178,198),Point(179,196),Point(182,188),Point(182,177),Point(178,167),Point(170,150),Point(163,138),Point(152,130),Point(143,129),Point(140,131),Point(129,136),Point(126,139)],

  "check": [Point(91,185),Point(93,185),Point(95,185),Point(97,185),Point(100,188),Point(102,189),Point(104,190),Point(106,193),Point(108,195),Point(110,198),Point(112,201),Point(114,204),Point(115,207),Point(117,210),Point(118,212),Point(120,214),Point(121,217),Point(122,219),Point(123,222),Point(124,224),Point(126,226),Point(127,229),Point(129,231),Point(130,233),Point(129,231),Point(129,228),Point(129,226),Point(129,224),Point(129,221),Point(129,218),Point(129,212),Point(129,208),Point(130,198),Point(132,189),Point(134,182),Point(137,173),Point(143,164),Point(147,157),Point(151,151),Point(155,144),Point(161,137),Point(165,131),Point(171,122),Point(174,118),Point(176,114),Point(177,112),Point(177,114),Point(175,116),Point(173,118)]
}

class Recogniser:

  def __init__(self, use_predefined_templates: bool=True) -> None:
    self.templates: list[Template] = []

    if use_predefined_templates:
      for key, value in predefined_gestures.items():
        self.add_template(key, value)

  def recognise(self, points: list[Point]) -> tuple[Template, float]:
    '''
      important note: length of list must be 2 or greater although it makes no sense to evaluate a path with 2 points. also the points must differentiate in x-axis and y-axis. e.g. point(10,10) and point(10,10) are not allowed because it results in a 0 length bounding box, throwing a division by zero error.
    '''
    if not _evaluate_list(points):
      return (None, None)

    points = _convert_points(points)

    b = float("infinity")
    found_template: Template = None

    for template in self.templates:
      d = _distance_at_best_angle(points, template, Config.PHI, Config.THETA_NEG, Config.THETA_POS, Config.THETA_DELTA)

      if d < b:
        b = d
        found_template = template

    score = 1.0 - (b / Config.HALF_DIAGONAL)
    
    return (found_template, score)

  def add_template(self, name: str, points: list[Point]) -> bool:
    '''
      adding _mirror_points which mirrors all points along the x-axis so that you avoid the 1$ recogniser limitation where only one draw direction for a gesture works
    '''
    if not _evaluate_list(points):
      return False

    converted_points = _convert_points(points)
    mirrored_points = _mirror_points(converted_points)
    
    template = Template(len(self.templates), name, converted_points)
    mirrored_template = Template(len(self.templates)+1, name, mirrored_points)

    self.templates.append(template)
    self.templates.append(mirrored_template)
    
    return True