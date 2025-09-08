class IntersectionConfig:
    def __init__(self, config):
        self.video_path = config['video_path']
        self.date = config['date']
        self.start_time = config['start_time']
        self.start_time_seconds = config['start_time_seconds']
        self.approaches = config['approaches']
        self.users = ['passenger_vehicle', 'bus', 'articulated_truck',  'single_unit_truck', 'motorcycle', 'bicycle', 'pedestrian']
