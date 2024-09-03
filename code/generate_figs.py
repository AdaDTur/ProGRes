import string
import Levenshtein
import numpy as np
import matplotlib.pyplot as plt

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

#for getting figures
error_rates = {}
combined_dict = {}

error_rates = {}
plt.figure(figsize=(10, 6))
models = ["model-name"]

for mod in models:
  file_path = "file_path"
  preds = open(file_path, "r")
  pred_lines = preds.readlines()
  error_rates[mod] = {}

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
        llm_score = -100 #set to some lower bound
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
    ground_dict = {}

    transcript = open("test_transcript.txt", "r")
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
    error_rates[mod][beta] = error_rate
    print(f"Error rates computed for: {mod}")

labels = ["model-name"]
label_ind = 0
for sub_dict in error_rates:
  alphas = list(reversed(list(error_rates[sub_dict].keys())))
  wers = [float(error_rates[sub_dict][key]) * 100 for key in alphas]
  plt.plot(alphas, wers, marker='o', label=labels[label_ind])
  label_ind += 1
plt.legend(loc='upper center', bbox_to_anchor=(1.2, 1.02))
plt.xlabel('LLM Weight')
plt.ylabel('Word Error Rate (%)')
plt.title('Change in Word Error Rate as LLM Weight Increases')
plt.grid(True)
plt.savefig('fig.pdf', bbox_inches = "tight")
plt.show()
