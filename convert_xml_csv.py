import os, csv, uuid
import xml.etree.ElementTree as ET

SCRIPT_DIR = os.path.dirname(__file__)
path = os.path.join(SCRIPT_DIR, "xml_logs")

for root, subdirs, files in os.walk(path):
  if 'ipynb_checkpoint' in root:
      continue
  
  if len(files) == 0:
    continue

  for f in files:
    if not f.endswith(".xml"):
      continue

    fname = f.split('.')[0]
    label = fname[:-2]
    
    xml_root = ET.parse(f'{root}/{f}').getroot()
    
    points = []
    counter = 0

    header = ["idx", "label", "x", "y", "timestamp"]

    for element in xml_root.findall('Point'):
      idx = counter
      x = element.get('X')
      y = element.get('Y')
      t = element.get('T')
      
      points.append([idx, label, x, y, t])
      counter += 1
        
    path = os.path.join(SCRIPT_DIR, f"./raw_logs/{label}")
    if not os.path.isdir(path):
      os.mkdir(path)

    idx = uuid.uuid4()
    path = os.path.join(SCRIPT_DIR, f"./raw_logs/{label}/{idx}.csv")
    with open(path, "w") as csv_file:
      writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE)
      writer.writerow(header)
      writer.writerows(points)