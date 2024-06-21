import os
from openai import OpenAI
import pandas as pd
import re

asr_data = open('test_nbest.txt', 'r')
asr_lines = asr_data.readlines()

prev_id = ""
hyp_dict = {}

for line in asr_lines:
    line_split = line.split('\t')
    if len(line_split) < 2:
        continue
    id = line_split[0]
    text = line_split[2]

    if id != prev_id:
        prev_id = id
        hyp_dict[id] = [text]
    else:
        hyp_dict[id].append(text)

output = open('output.txt', 'w')

client = OpenAI(
    api_key='api-key',
)

def extract_sentence(sentence):
    pattern = r'<(.*?)>'
    matches = re.findall(pattern, sentence)
    return matches

for id in hyp_dict:
    prompt = "prompt"
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    answer = extract_sentence(str(chat_completion.choices[0].message.content))
    if answer is None or len(answer) < 1:
        answer = "NANNANNAN"
    else:
        answer = answer[0].strip()
    output.write(id + '\t' + answer + '\n')
    if answer not in hyp_dict[id]:
        hyp_dict[id].append(answer)

output.close()