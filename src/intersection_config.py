class IntersectionConfig:
    def __init__(self, config):
        self.video_paths = config['video_paths']
        self.date = config['date']
        self.start_time = config['start_time']
        self.collection_type = config['collection_type']
        self.approaches = config['approaches']
        self.vehicle_classifications = ['passenger_vehicle', 'bus', 'LRV', 'articulated_truck',
                                        'single_unit_truck', 'motorcycle', 'bicycle', 'scooter']
        self.vru_classifications = ['pedestrian', 'bicycle', 'scooter']

        self.timestamps = config.get('timestamps')
        self.last_actions = config.get('last_actions', {})

        self.icons = {'erase': 'data/icons/eraser.png',
                      'forward': 'data/icons/forward.png',
                      'intersection': 'data/icons/intersection.png',
                      'rewind': 'data/icons/rewind.png',
                      'rotate': 'data/icons/rotate.png',
                      'playPause': 'data/icons/playPause.png',
                      'speed': 'data/icons/speed.png'}


