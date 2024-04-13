import re
import csv
import numpy as np

result_input_path = './pcsp_results'
csv_output_path = './betting_simulation/new_probabilities'
seasons = ['1516', '1617', '1718', '1819', '1920', '2021']
input_file_name = {'1516': '20152016_results', '1617': '20162017_results', '1718': '20172018_results', 
                   '1819': '20182019_results', '1920': '20192020_results', '2021': '20202021_results'}

def softmax(x):
  e_x = np.exp(x - np.max(x))
  return e_x / e_x.sum()

for season in seasons:
  with open(f'{result_input_path}/{input_file_name[season]}.txt', 'r') as f:
    result = f.read()
    matches = re.findall(r'(.{5})_home\.pcsp', result)
    probs = re.findall(r'\[(.*?), (.*?)\];', result)
    probs_softmax = []
    for i in range(len(matches)):
      away_prob = (float(probs[2*i][0]) + float(probs[2*i][1]))/2
      home_prob = (float(probs[2*i+1][0]) + float(probs[2*i+1][1]))/2
      prob_softmax = softmax(np.array([home_prob, away_prob]))
      probs_softmax.append(prob_softmax[0])

  with open(f'{csv_output_path}/{season}.csv', 'w', newline='') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['match_url', 'home_prob_softmax'])
    for row in zip(matches, probs_softmax):
      csv_writer.writerow([f'https://www.premierleague.com/match/{row[0]}', f'{row[1]}'])
