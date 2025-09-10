class IntersectionConfig:
    def __init__(self, config):
        self.video_path = config['video_path']
        self.date = config['date']
        self.start_time = config['start_time']
        self.start_time_seconds = config['start_time_seconds']
        self.collection_type = config['collection_type']
        self.approaches = config['approaches']
        self.vehicle_classifications = ['passenger_vehicle', 'bus', 'LRV', 'articulated_truck',
                                        'single_unit_truck', 'motorcycle', 'bicycle', 'scooter']
        self.vru_classifications = ['pedestrian', 'bicycle', 'scooter']
        self.icons = {'erase':'data/icons/eraser.png',
                      'forward': 'data/icons/forward.png',
                      'intersection': 'data/icons/intersection.png',
                      'rewind': 'data/icons/rewind.png',
                      'rotate': 'data/icons/rotate.png',
                      'playPause': 'data/icons/playPause.png',
                      'speed': 'data/icons/speed.png'}
