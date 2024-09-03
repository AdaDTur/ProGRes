import numpy as np
import Levenshtein
import matplotlib.pyplot as plt
import string

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

def wer(truth, hypothesis):
  truth_words = truth.split()
  hypothesis_words = hypothesis.split()
  distance = Levenshtein.distance(truth_words, hypothesis_words)
  return distance, len(truth_words)

#this portion of code is for getting wer with combining asr and llm scores
error_rates = {}
combined_dict = {}


error_rates = {}
plt.figure(figsize=(10, 6))

file_path = "file_path"
preds = open(file_path, "r")
pred_lines = preds.readlines()
error_rates = {}

for alpha in np.arange(0, 1.1, 0.1):
  beta = 1 - alpha
  prev_id = ""
  count = 0
  for line in pred_lines:
    if line == '\n':
      continue
    line_split = line.split('\t')

    id = line_split[0]
    text = line_split[1]
    if text == 'NANNANNAN':
      continue
    asr_score = float(line_split[2])
    llm_score = float(line_split[3])
    if llm_score == 'nan':
      llm_score = -100 #set to some lower bound of choice, doesn't affect wer much

    #combined here
    combined_score = ((alpha * asr_score) + (beta * llm_score))
    if id != prev_id or prev_id == "":
      count += 1
      combined_dict[id] = {}
      combined_dict[id]["text"] = text
      combined_dict[id]["score"] = combined_score
      prev_id = id
    else:
      if combined_score > combined_dict[id]["score"]: #this depends on if scores are positive or negative
        combined_dict[id]["text"] = text
        combined_dict[id]["score"] = combined_score

  #here we compute error
  ground_dict = {}
  transcript = open("dev_transcript.txt", "r")
  ground_truth_array = transcript.readlines()
  for i in ground_truth_array:
    j = i.split('\t')
    id = j[0]
    text = j[1]
    text = remove_punctuation(text).lower()
    ground_dict[id] = text

  err = 0
  tot = 0
  for id in ground_dict:
    if id not in combined_dict:
      continue
    pred_text = remove_punctuation(combined_dict[id]["text"]).lower()
    anerr, atot = wer(ground_dict[id], pred_text)
    err += anerr
    tot += atot

  error_rate = err/tot
  error_rates[alpha, beta] = error_rate
  print(str(alpha), str(beta), "Word Error Rate:", error_rate, "Num errors:", err, "Total number of words:", tot)
print("MIN", str(min(error_rates, key=error_rates.get)), str(error_rates[min(error_rates, key=error_rates.get)]))

#this is for computing wer with a 1-best file, no combination, for txt files
transcript = open("test_transcript.txt", "r")
ground_truth_array = transcript.readlines()
ground_truth = [i.split('\t')[1] for i in ground_truth_array]


#with file
preds = open("prompt_only.txt", "r")
speech_output_array = preds.readlines()
speech_output = [i.split('\t')[1] for i in speech_output_array if len(i.split('\t')) > 1]
err = 0
tot = 0

for i in range(len(ground_truth)):

  #with file
  ground_truth[i] = remove_punctuation(ground_truth[i])
  speech_output[i] = remove_punctuation(speech_output[i])
  ground_truth[i] = ground_truth[i].lower()
  speech_output[i] = speech_output[i].lower()

  anerr, atot = wer(ground_truth[i], speech_output[i])
  err += anerr
  tot += atot

error_rate = err/tot
print("Word Error Rate:", error_rate, "Num errors:", err, "Total number of words:", tot)
