# Traffic Data Collector


To open the app: 
- install conda
- open terminal/cmd and change directory to the root folder of the project. Run the following commands:
  - install environment.yml
  `conda env create -f environment.yml`
  - activate the environment `conda activate traffic_counter`
  - run `python main.py`
  
- Alternatively, you can make a new environment and manually install PyQt6, OpenCV, and Numpy.

Before you count volume:
- get familiar with the intersection properties including 
    - direction of each leg
    - allowable movements for each approach
    - direction of each sidewalk
