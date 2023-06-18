## Implementing the $1 Gesture Recognizer

- algorithm is based on https://depts.washington.edu/acelab/proj/dollar/dollar.pdf pseudocode
- also added 5 default gesture templates from https://depts.washington.edu/acelab/proj/dollar/dollar.js
- recogniser can add additional templates
- templates are mirror along the y-axis so that the gesture can be drawn clock- and counter-clockwise removing 1$ recogniser limitation
- before recognition, the list of points is evaluated if width/height of a bounding box would be zero because it would result in division by zero later

## Comparing Gesture Recognizers

- added convert_xml_csv.py to convert xml_logs to better structured csv files which can be found in raw_logs
- created a dataset with create_dataset.py which can be fou nd in dataset split into a test folder with 10 logs of each class and train which contains the remaining data
- unistroke-gesture.ipynb contains 5 lstm models with different hyperparameters and 2 different recogniser models along with a evaluation at the end
- trained model along with labels were saved so that it could be used in a later application

## Gesture Detection Game

- gesture-application.py contains the game along with a config file
- it is a memory game where each card hides a written gesture
- first, the computer shows the player a sequence of cards with a written gesture to memorise
- after that, the player must draw the gestures on the according cards and in sequence
- if correct, the computer plays the sequence extended by the next element starting with the first element
- if wrong, the game ends
- ends if all cards are correctly guessed
- the sequence and gestures are random each game
- the game only accepts gestures after the sequence is played otherwise gestures are ignored or lead to sequence interruption
- the state of the game is indicated in the top left text
- the last recognised gesture is indicated in the bot left text
- the gesture must not be extaclty within the card; it can overlap because the game checks what card contains the most points and chooses it this way

### CONTROLS:

- the game can be restarted by drawing CHECK
- the game can be quit by drawing X
- cards use following gestures: TRIANGLE, RECTANGLE, CIRCLE
