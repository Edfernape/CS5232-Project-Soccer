# CS5232 Project
 
1. Run `python3 generate_pcsp.py` (or `python generate_pcsp.py`). This creates a `pcsp` folder and a sub-folder for each season. Within each season folder, two pscp files are generated for each match, corresponding to the away team and the home team. Ensure that `pandas` is installed.
2. Execute all pcsp files and put result files in the `pcsp_results` folder. 
3. Run `python3 generate_probabilities.py` (or `python generate_probabilities.py`). This writes generated probabilities to csv files under the `betting_simulation/new_probabilities` folder. 
4. Navigate to `./betting_simulation/` and run `python3 ./simulate.py` (or `python ./simulate.py`) to get the betting profits.