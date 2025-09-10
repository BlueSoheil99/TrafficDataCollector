class IntersectionConfig:
    def __init__(self, config, from_cache=False):
        # self.video_path = config['video_path'] # TODO remove the line below later
        self.video_path = ('/Users/soheil/Library/CloudStorage/OneDrive-UW/0 Research/Sound '
                             'Transit Project/Codes/TrafficDataCollector/data/0_0_1730564065032_10003_10026_0.mp4')
        self.date = config['date']
        self.start_time = config['start_time']
        self.collection_type = config['collection_type']
        self.approaches = config['approaches']
        self.vehicle_classifications = ['passenger_vehicle', 'bus', 'LRV', 'articulated_truck',
                                        'single_unit_truck', 'motorcycle', 'bicycle', 'scooter']
        self.vru_classifications = ['pedestrian', 'bicycle', 'scooter']

        self.timestamps = config.get('timestamps')
        self.last_action = config.get('last_action')

        self.icons = {'erase': 'data/icons/eraser.png',
                      'forward': 'data/icons/forward.png',
                      'intersection': 'data/icons/intersection.png',
                      'rewind': 'data/icons/rewind.png',
                      'rotate': 'data/icons/rotate.png',
                      'playPause': 'data/icons/playPause.png',
                      'speed': 'data/icons/speed.png'}


