class IntersectionConfig:
    def __init__(self, config):
        self.video_paths = config.get('video_paths')
        self.collection_type = config.get('collection_type')
        self.data_path = config.get('data_path')

        self.date = config.get('date')
        self.start_time = config.get('start_time')
        self.approaches = config.get('approaches')

        self.movements = ['Left', 'Through', 'Right']
        self.vehicle_classifications = ['Passenger_vehicle', 'Bus',  'Van', 'Single_unit_truck', 'Articulated_truck',
                                        'LRV', 'Motorcycle', 'Bicycle', 'Scooter, etc.']
        # self.vru_classifications = ['pedestrian', 'bicycle', 'scooter']
        self.vru_classifications = ['Pedestrian', 'Bicycle', 'Mobility Aid User', 'Personal Mobility Device']

        self.timestamps = config.get('timestamps')
        self.last_actions = config.get('last_actions', {})

        self.icons = {'erase': 'data/icons/eraser.png',
                      'forward': 'data/icons/forward.png',
                      'intersection': 'data/icons/intersection.png',
                      'rewind': 'data/icons/rewind.png',
                      'rotate': 'data/icons/rotate.png',
                      'playPause': 'data/icons/playPause.png',
                      'speed': 'data/icons/speed.png'}


