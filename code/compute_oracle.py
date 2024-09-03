import Levenshtein
import string
import pandas as pd

def wer(truth, hypothesis):
  truth_words = truth.split()
  hypothesis_words = hypothesis.split()
  distance = Levenshtein.distance(truth_words, hypothesis_words)
  return distance, len(truth_words)

def remove_punctuation(text):
    text = text.replace(" m ", "m ")
    text = text.replace(" t ", "t ")
    text = text.replace(" s ", "s ")
    text = text.replace(" d ", "d ")
    text = text.replace(" ll ", "ll ")
    text = text.replace(" re ", "re ")
    text = text.replace(" ve ", "ve ")
    text = text.replace("-", " ")
    translator = str.maketrans('', '', string.punctuation)
    text_without_punctuation = text.translate(translator)
    return text_without_punctuation

#with files
transcript = open("test_transcript.txt", "r")
ground_truth_array = transcript.readlines()
speech_output = {}
ground_truth = {}
preds = open("test_predictions.txt", "r")
speech_output_array = preds.readlines()

for line in speech_output_array:
  line_split = line.split('\t')
  id = line_split[0]
  text = remove_punctuation(line_split[1]).lower()
  score = line_split[2]
  if id not in speech_output:
    speech_output[id] = [text]
  else:
    speech_output[id].append(text)

for line in ground_truth_array:
  line_split = line.split('\t')
  id = line_split[0]
  text = line_split[1]
  ground_truth[id] = text

err = 0
tot = 0
prompt_count = 0
minindex = 0
for id in ground_truth:
  if id not in speech_output:
    continue
  ground_text = remove_punctuation(ground_truth[id]).lower()
  minerr = len(ground_text)
  for j in range(len(speech_output[id])):
    pred_text = remove_punctuation(speech_output[id][j]).lower()
    anerr, atot = wer(ground_text, pred_text)
    if anerr < minerr:
      minerr = anerr
      minindex = j
  err += minerr
  tot += atot
error_rate = err/tot

print("Word Error Rate:", error_rate, "Num errors:", err, "Total number of words:", tot)

#with csv
transcript = {}
preds = {}
df = pd.read_csv('test_transcript.csv', sep='\t')

for index, row in df.iterrows():
  row_split = row[0].split(',')
  if len(row_split) != 3:
    kept = row_split[:2]
    split_sent = ','.join(row_split[2:])
    row_split = kept + [split_sent]
  path = row_split[1]
  id = path.split('/')[-1][:-4]
  sentence = row_split[2]
  transcript[id] = sentence

pdf = pd.read_csv('test_nbest.csv', sep='\t')
for index, row in pdf.iterrows():
  id = row['id']
  if type(row['hyp']) == float:
    row['hyp'] = ''
  sentence = row['hyp'].lower()
  if id in preds:
    preds[id].append(sentence)
  else:
    preds[id] = [sentence]

err = 0
tot = 0
prompt_count = 0
minindex = 0

for id in transcript:
  if id not in preds:
    continue
  trans = remove_punctuation(transcript[id]).lower()
  minerr = len(trans.split())
  for i in range(len(preds[id])):
    pred = preds[id][i]
    pred = remove_punctuation(pred).lower()
    anerr, atot = wer(trans, pred)
    if anerr < minerr:
      minerr = anerr
      minindex = i
  if minindex != 0 and minindex != :
    x=0
  err += minerr
  tot += atot

error_rate = err/tot
print("Word Error Rate:", error_rate, "Num errors:", err, "Total number of words:", tot)
