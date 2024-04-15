import os
import pandas as pd

POSITION = {'L':6, 'LR':7, 'CL':8, 'C':9, 'CR':10, 'RL':11, 'R':12}
EMPTY_POSITION = [-1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1]

def get_seq_formatted(formation, sequence):
  base = 0
  pos_formatted = []
  seq_formatted = []
  for num in formation:
    num = int(num)
    curr_seq = []
    curr_pos = EMPTY_POSITION[:]
    for i in range(num):
      curr_seq.append(sequence[base+i])
      curr_pos[POSITION[sequence[base+i]]] = 1
    base += num
    seq_formatted.append(curr_seq)
    pos_formatted.append(curr_pos)
  return pos_formatted, seq_formatted

def get_pos_grid(seq_formatted):
  position_grid = []
  for i in range(7):
    position_grid.append(EMPTY_POSITION[:])
    if i == 0 or i == 6:
      position_grid[i][9] = 1
  if len(seq_formatted) == 3:
    position_grid[1] = seq_formatted[0]
    position_grid[3] = seq_formatted[1]
    position_grid[5] = seq_formatted[2]
  elif len(seq_formatted) == 4:
    position_grid[1] = seq_formatted[0]
    position_grid[2] = seq_formatted[1]
    position_grid[3] = seq_formatted[2]
    position_grid[5] = seq_formatted[3]
  elif len(seq_formatted) == 5:
    position_grid[1] = seq_formatted[0]
    position_grid[2] = seq_formatted[1]
    position_grid[3] = seq_formatted[2]
    position_grid[4] = seq_formatted[3]
    position_grid[5] = seq_formatted[4]
  return position_grid

def get_grid_formatted(grid):
  res = []
  vars = ['atkKepPos', 'atkDefPos', 'atkMidDefPos', 'atkMidPos', 'atkMidForPos', 'atkForPos', 'defKepPos']
  for i in range(len(vars)):
    _str = f'var {vars[i]} = {grid[i]};'
    res.append(_str)
  return '\n'.join(res)

def get_players(ids, rating_df):
  players = []
  for id in ids.split(','):
    id = int(float(id))
    players.append(rating_df[rating_df['sofifa_id'] == id])
  return players

def get_def(atk_seq, def_seq, atk_players, def_players):
  prob_lose = 0 # avg(max(standing tackle, sliding tackle, interception))
  deffor_seq = def_seq[-1]
  for i in range(len(deffor_seq)):
    player = def_players[len(def_players)-i-1]
    prob_lose += max(player['defending_standing_tackle'].values[0], player['defending_sliding_tackle'].values[0], player['mentality_interceptions'].values[0])
  prob_lose /= len(deffor_seq)

  atkdef = []
  atkdef_seq = atk_seq[0]
  for i in range(len(atkdef_seq)):
    atkdef_player = atk_players[i+1]
    sp = atkdef_player['attacking_short_passing'].values[0]
    lp = atkdef_player['skill_long_passing'].values[0]
    _str = f'[pos[{atkdef_seq[i]}] == 1]Def({sp}, {lp}, {int(prob_lose)}, {atkdef_seq[i]})'
    atkdef.append(_str)
  return ' [] '.join(atkdef)

def get_mid(atk_seq, def_seq, atk_players, def_players):
  atkmiddef, atkmid, atkmidfor = [], [], []
  prob_lose = 0
  def_start = len(def_seq[0])+1
  def_end = 11-len(def_seq[-1])
  for i in range(def_start, def_end):
    player = def_players[i]
    prob_lose += max(player['defending_standing_tackle'].values[0], player['defending_sliding_tackle'].values[0], player['mentality_interceptions'].values[0])
  prob_lose /= (def_end-def_start)

  layer = len(atk_seq)
  if layer == 3:
    mid_seq = atk_seq[1]
    for i in range(len(mid_seq)):
      mid_player = atk_players[i+len(atk_seq[0])+1]
      sp = mid_player['attacking_short_passing'].values[0]
      lp = mid_player['skill_long_passing'].values[0]
      ls = mid_player['power_long_shots'].values[0]
      _str = f'[pos[{mid_seq[i]}] == 1]Mid({sp}, {lp}, {ls}, {int(prob_lose)}, {mid_seq[i]})'
      atkmid.append(_str)
    mid_str = ' [] '.join(atkmid)
    return f'AtkMidDef = Skip;\nAtkMid = {mid_str};\nAtkMidFor = Skip;'
  elif layer == 4:
    middef_seq = atk_seq[1]
    mid_seq = atk_seq[2]
    for i in range(len(middef_seq)):
      mid_player = atk_players[i+len(atk_seq[0])+1]
      sp = mid_player['attacking_short_passing'].values[0]
      lp = mid_player['skill_long_passing'].values[0]
      ls = mid_player['power_long_shots'].values[0]
      _str = f'[pos[{middef_seq[i]}] == 1]MidDef({sp}, {lp}, {ls}, {int(prob_lose)}, {middef_seq[i]})'
      atkmiddef.append(_str)
    middef_str = ' [] '.join(atkmiddef)
    for i in range(len(mid_seq)):
      mid_player = atk_players[i+len(atk_seq[0])+len(middef_seq)+1]
      sp = mid_player['attacking_short_passing'].values[0]
      lp = mid_player['skill_long_passing'].values[0]
      ls = mid_player['power_long_shots'].values[0]
      _str = f'[pos[{mid_seq[i]}] == 1]Mid({sp}, {lp}, {ls}, {int(prob_lose)}, {mid_seq[i]})'
      atkmid.append(_str)
    mid_str = ' [] '.join(atkmid)
    return f'AtkMidDef = {middef_str};\nAtkMid = {mid_str};\nAtkMidFor = Skip;'
  elif layer == 5:
    middef_seq = atk_seq[1]
    mid_seq = atk_seq[2]
    midfor_seq = atk_seq[3]
    for i in range(len(middef_seq)):
      mid_player = atk_players[i+len(atk_seq[0])+1]
      sp = mid_player['attacking_short_passing'].values[0]
      lp = mid_player['skill_long_passing'].values[0]
      ls = mid_player['power_long_shots'].values[0]
      _str = f'[pos[{middef_seq[i]}] == 1]MidDef({sp}, {lp}, {ls}, {int(prob_lose)}, {middef_seq[i]})'
      atkmiddef.append(_str)
    middef_str = ' [] '.join(atkmiddef)
    for i in range(len(mid_seq)):
      mid_player = atk_players[i+len(atk_seq[0])+len(middef_seq)+1]
      sp = mid_player['attacking_short_passing'].values[0]
      lp = mid_player['skill_long_passing'].values[0]
      ls = mid_player['power_long_shots'].values[0]
      _str = f'[pos[{mid_seq[i]}] == 1]Mid({sp}, {lp}, {ls}, {int(prob_lose)}, {mid_seq[i]})'
      atkmid.append(_str)
    mid_str = ' [] '.join(atkmid)
    for i in range(len(midfor_seq)):
      mid_player = atk_players[i+len(atk_seq[0])+len(middef_seq)+1]
      sp = mid_player['attacking_short_passing'].values[0]
      lp = mid_player['skill_long_passing'].values[0]
      ls = mid_player['power_long_shots'].values[0]
      _str = f'[pos[{midfor_seq[i]}] == 1]MidFor({sp}, {lp}, {ls}, {int(prob_lose)}, {midfor_seq[i]})'
      atkmidfor.append(_str)
    midfor_str = ' [] '.join(atkmidfor)
    return f'AtkMidDef = {middef_str};\nAtkMid = {mid_str};\nAtkMidFor = {midfor_str};'
  return ''

def get_for(atk_seq, def_seq, atk_players, def_players):
  prob_lose = 0 # avg(max(standing tackle, sliding tackle, interception))
  defdef_seq = def_seq[0]
  for i in range(len(defdef_seq)):
    player = def_players[i+1]
    prob_lose += max(player['defending_standing_tackle'].values[0], player['defending_sliding_tackle'].values[0], player['mentality_interceptions'].values[0])
  prob_lose /= len(defdef_seq)

  pk = 0 # avg(mentality_aggression) - mentality_aggression
  for i in range(len(defdef_seq)):
    player = def_players[i+1]
    pk += player['mentality_aggression'].values[0]
  pk /= len(defdef_seq)

  atkfor = []
  atkfor_seq = atk_seq[-1]
  for i in range(len(atkfor_seq)):
    atkfor_player = atk_players[len(atk_players)-len(atkfor_seq)+i]
    fi = atkfor_player['attacking_finishing'].values[0]
    ls = atkfor_player['power_long_shots'].values[0]
    vo = atkfor_player['attacking_volleys'].values[0]
    hd = atkfor_player['attacking_heading_accuracy'].values[0]
    _pk = pk - atkfor_player['mentality_aggression'].values[0]
    #_pk = 0 if _pk < 0 else int(_pk)
    _str = f'[pos[{atkfor_seq[i]}] == 1]For({fi}, {ls}, {vo}, {hd}, {int(prob_lose)}, {atkfor_seq[i]}, {_pk})'
    atkfor.append(_str)
  return ' [] '.join(atkfor)

def get_kep(atk_players, def_players):
  atkkep_player = atk_players[0]
  gk_kick = atkkep_player['goalkeeping_kicking'].values[0]
  defkep_player = def_players[0]
  gk_handle = defkep_player['goalkeeping_handling'].values[0]
  atkkep = f'[pos[C] == 1]Kep_1({gk_kick}, {gk_kick}, C)'
  defkep = f'[pos[C] == 1]Kep_2({gk_handle}, C)'
  return atkkep, defkep

if not os.path.exists('./pcsp'):
  os.mkdir('./pcsp')
years = ['20152016', '20162017', '20172018', '20182019', '20192020', '20202021']
for year in years:
  if not os.path.exists(f'./pcsp/{year}'):
    os.mkdir(f'./pcsp/{year}')
  match_df = pd.read_csv(f'Datasets/matches/epl_matches_{year}.csv')
  rating_df = pd.read_csv(f'Datasets/ratings/epl_ratings_{year}.csv')
  for _, match in match_df.iterrows():
    match_id = match['match_url'][-5:]
    # print(match_id)
    away_formation = match['away_formation'].rstrip('-0').split('-')
    home_formation = match['home_formation'].rstrip('-0').split('-')
    away_sequence = match['away_sequence'][2:].split(',')
    home_sequence = match['home_sequence'][2:].split(',')
    away_ids = match['away_xi_sofifa_ids']
    home_ids = match['home_xi_sofifa_ids']

    away_pos_formatted, away_seq_formatted = get_seq_formatted(away_formation, away_sequence)
    home_pos_formatted, home_seq_formatted = get_seq_formatted(home_formation, home_sequence)

    away_grid = get_pos_grid(away_pos_formatted)
    away_grid_formatted = get_grid_formatted(away_grid)
    home_grid = get_pos_grid(home_pos_formatted)
    home_grid_formatted = get_grid_formatted(home_grid)
    away_players = get_players(away_ids, rating_df)
    home_players = get_players(home_ids, rating_df)

    flagMidDef = f'var isMidDefOccupied = {"false" if len(away_seq_formatted)==3 else "true"};'
    flagMidFor = f'var isMidForOccupied = {"true" if len(away_seq_formatted)==5 else "false"};'
    atkdef = get_def(away_seq_formatted, home_seq_formatted, away_players, home_players)
    atkmid = get_mid(away_seq_formatted, home_seq_formatted, away_players, home_players)
    atkfor = get_for(away_seq_formatted, home_seq_formatted, away_players, home_players)
    atkkep, defkep = get_kep(away_players, home_players)
    with open(r'template_penalty_kick.pcsp', 'r') as file: 
      data = file.read() 
      data = data.replace('__flags__', flagMidDef+'\n'+flagMidFor)
      data = data.replace('__grid__', away_grid_formatted)
      data = data.replace('__AtkKep__', atkkep)
      data = data.replace('__AtkDef__', atkdef)
      data = data.replace('__AtkMid__', atkmid)
      data = data.replace('__AtkFor__', atkfor)
      data = data.replace('__DefKep__', defkep)
    file_name = f'./pcsp/{year}/{match_id}_away.pcsp'
    with open(file_name, 'w') as file:
      file.write(data)

    flagMidDef = f'var isMidDefOccupied = {"false" if len(home_seq_formatted)==3 else "true"};'
    flagMidFor = f'var isMidForOccupied = {"true" if len(home_seq_formatted)==5 else "false"};'
    atkdef = get_def(home_seq_formatted, away_seq_formatted, home_players, away_players)
    atkmid = get_mid(home_seq_formatted, away_seq_formatted, home_players, away_players)
    atkfor = get_for(home_seq_formatted, away_seq_formatted, home_players, away_players)
    atkkep, defkep = get_kep(home_players, away_players)
    with open(r'template_penalty_kick.pcsp', 'r') as file: 
      data = file.read() 
      data = data.replace('__flags__', flagMidDef+'\n'+flagMidFor)
      data = data.replace('__grid__', home_grid_formatted)
      data = data.replace('__AtkKep__', atkkep)
      data = data.replace('__AtkDef__', atkdef)
      data = data.replace('__AtkMid__', atkmid)
      data = data.replace('__AtkFor__', atkfor)
      data = data.replace('__DefKep__', defkep)
    file_name = f'./pcsp/{year}/{match_id}_home.pcsp'
    with open(file_name, 'w') as file:
      file.write(data)
