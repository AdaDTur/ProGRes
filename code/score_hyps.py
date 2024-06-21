# -*- coding: utf-8 -*-
"""
Colab Notebook available at: https://colab.research.google.com/drive/1L9Cnp8XlUEtaSSNktOWxfwmkwo0do7gE?usp=sharing
"""
import pandas as pd
import os
import numpy as np
from minicons import scorer

ilm_model = scorer.IncrementalLMScorer("hf-model-name", 'cuda')

prompt_results = open("prompts.txt", "r")
output = open("output.txt", "w")

asr_dict = {}
prompt_lines = prompt_results.readlines()

asr_results = open('dev_nbest.txt', 'r')
asr_lines = asr_results.readlines()

for line in asr_lines:
  line_split = line.split('\t')
  if len(line_split) < 3:
    continue
  text = line_split[1].lower()
  id = line_split[0]
  text = line_split[2].lower()
  score = line_split[4].strip()
  if id not in asr_dict:
    asr_dict[id] = [[text, score]]
  else:
    asr_dict[id].append([text, score])

for line in prompt_lines:
  line_split = line.split("\t")
  id = line_split[0]
  sentence = line_split[1].lower()
  asr_dict[id].append([sentence, asr_dict[id][0][0]])

for ind, id in enumerate(asr_dict):
  for i in range(len(asr_dict[id])):
    sentence = asr_dict[id][i][0].strip()
    asr_score = asr_dict[id][i][1]
    llm_score = ilm_model.sequence_score(sentence, reduction=lambda x: x.mean(0).item())
    output.write(str(id) + "\t" + sentence.strip() + "\t" + str(asr_score).strip() + "\t" + str(llm_score).strip() + "\n")

output.close()