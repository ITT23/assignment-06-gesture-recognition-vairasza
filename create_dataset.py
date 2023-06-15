import os, random, shutil

SCRIPT_DIR = os.path.dirname(__file__)
ROOT = os.path.join(SCRIPT_DIR, "raw_logs/")

TEST_PATH = os.path.join(SCRIPT_DIR, "dataset/test")
TRAIN_PATH = os.path.join(SCRIPT_DIR, "dataset/train")
K = 10
SEED = 42

def add_file(origin_path, destination_folder, file_name):
  if not os.path.isdir(destination_folder):
    os.mkdir(destination_folder)

  destination_path = os.path.join(destination_folder, file_name)

  shutil.copy(origin_path, destination_path) #copy file from raw_logs to train or test

for root, _, files in os.walk(ROOT):
  class_length = len(files)
  class_name = os.path.basename(root)

  if class_length < 10: #we dont want to create a testset if there are only 10 gestures available
    continue
  
  random.seed(SEED) #to reproduce results, set a fix seed
  indexes = random.sample(range(0, class_length), K) #get K random indexes from the list of files

  for key, file_name in enumerate(files):
    if not file_name.endswith(".csv"):
      continue

    origin_file = os.path.join(ROOT, class_name, file_name)

    if key in indexes:
      #add to dataset/test
      destination_folder = os.path.join(TEST_PATH, class_name)
      add_file(origin_file, destination_folder, file_name)

    else:
      #add to dataset/train
      destination_folder = os.path.join(TRAIN_PATH, class_name)
      add_file(origin_file, destination_folder, file_name)
