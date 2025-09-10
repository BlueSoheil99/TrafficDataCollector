import json
import os

from src.intersection_config import IntersectionConfig


class DataManager:
    def __init__(self, config:IntersectionConfig, data_dict_params:tuple):
        self.config = config
        if config.timestamps:
            self.timestamps = config.timestamps
            self.last_action = config.last_action
        else:
            self.timestamps = _create_memory(veh_classes=data_dict_params[0], vru_classes=data_dict_params[1],
                                             movements=data_dict_params[2], approaches=self.config.approaches)
            self.last_action = 0.0 # todo update this

    def get_veh_counts(self, veh_class, movement, approach):
        return self.timestamps[approach][veh_class][movement]

    def get_vru_counts(self, vru_user, approach):
        return self.timestamps[approach][f'vru_{vru_user}']


    def update_veh_counts(self, veh_class, movement, approach, erase_mode:bool, entry_time):
        if erase_mode:
            if len(self.timestamps[approach][veh_class][movement]) > 0:
                deleted_entry = self.timestamps[approach][veh_class][movement].pop()
                print(f'--Erased Vehicle entry at time {deleted_entry} from {approach}:[{veh_class}, {movement}]')
                try:
                    last_entry = str(self.timestamps[approach][veh_class][movement][-1])
                except IndexError:
                    last_entry = '-'
            else:
                last_entry = '-'
            return last_entry
        else:
            print(f'++Added Vehicle entry at time {entry_time} for {approach}:[{veh_class}, {movement}]')
            self.timestamps[approach][veh_class][movement].append(_format_time(entry_time))
            return str(len(self.timestamps[approach][veh_class][movement]))


    def update_vru_counts(self, vru_class, approach, erase_mode:bool, entry_time):
        key = f'vru_{vru_class}'
        if erase_mode:
            if len(self.get_vru_counts(vru_class, approach)) > 0:
                deleted_entry = self.get_vru_counts(vru_class, approach).pop()
                print(f'--Erased VRU {vru_class} at time {deleted_entry} from {approach} approach')
                try:
                    new_label = str(self.get_vru_counts(vru_class, approach)[-1])
                except IndexError:
                    new_label = '-'
            else:
                new_label = '-'
        else:
            self.timestamps[approach][key].append(_format_time(entry_time))
            print(f'++Added VRU entry at time {entry_time} for {approach}-{vru_class}.')
            new_label = str(len(self.get_vru_counts(vru_class, approach)))
        return new_label


    def save_file(self, path, remove_cache=False):
        print(f"Saving file@ {path}")
        data = {
        'video': self.config.video_path,
        'date': self.config.date,
        'start_time':self.config.start_time,
        'last_action': self.last_action,
        'collection_type': self.config.collection_type,
        'approaches': self.config.approaches,
        'veh_classes':self.config.vehicle_classifications,
        'vru_classes':self.config.vru_classifications,
        'timestamps': self.timestamps
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        if remove_cache:
            try:
                os.remove('data/cache.json')
                print("--- found and deleted the cache")
            except FileNotFoundError:
                print("--- cache not found")



def _create_memory(veh_classes, vru_classes, movements, approaches):
    big_dict={}
    for approach in approaches:
        memory = {}
        for r in veh_classes:
            memory[r] = {c: [] for c in movements}
        for r in vru_classes:
            memory[f'vru_{r}'] = []
        big_dict[approach] = memory
    return big_dict

def _format_time(seconds):
    mins, secs = divmod(seconds, 60)
    formatted_time =  f'{int(mins):02d}:{secs:04.1f}'
    return formatted_time