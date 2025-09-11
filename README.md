# Traffic Data Collector


To open the app: 
- install conda
- open terminal/cmd and change directory to the root folder of the project. Run the following commands:
  - install environment.yml
  `conda env create -f environment.yml`
  - activate the environment `conda activate traffic_counter`
  - run `python main.py`

Before you count volume:
- get familiar with the intersection properties including 
    - direction of each leg
    - allowable movements for each approach
    - direction of each sidewalk
- (Not good) rotate the video if needed, to avoid confusion. For example, if SB vehicles are 
approaching the intersection from the right side of the frame