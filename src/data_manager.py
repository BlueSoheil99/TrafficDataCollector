import json
import os

from src.intersection_config import IntersectionConfig


class DataManager:
    def __init__(self, config:IntersectionConfig, data_dict_params:tuple):
        self.config = config
        if config.timestamps:
            self.timestamps = config.timestamps
            self.last_actions = config.last_actions
        else:
            self.timestamps = _create_memory(veh_classes=data_dict_params[0], vru_classes=data_dict_params[1],
                                             movements=data_dict_params[2], approaches=self.config.approaches)
            self.last_actions = {path: 0.0 for path in config.video_paths}

    def get_veh_counts(self, veh_class, movement, approach):
        return self.timestamps[approach][veh_class][movement]

    def get_vru_counts(self, vru_user, approach):
        return self.timestamps[approach][f'vru_{vru_user}']


    def update_veh_counts(self, veh_class, movement, approach, erase_mode:bool, entry_time_video):
        msg = None
        entry_time = _format_time(entry_time_video[0])
        vid_path = entry_time_video[1]
        if erase_mode:
            if len(self.timestamps[approach][veh_class][movement]) > 0:
                deleted_entry = self.timestamps[approach][veh_class][movement].pop()
                msg = f'➖Erased a {approach}:[{veh_class}, {movement}] entry @{deleted_entry}'
                self.last_actions[vid_path] = entry_time
                try:
                    last_entry = str(self.timestamps[approach][veh_class][movement][-1])
                except IndexError:
                    last_entry = '-'
            else:
                last_entry = '-'
            label = last_entry
        else:
            msg = f'➕Added a {approach}:[{veh_class}, {movement}] entry @{entry_time}'
            self.timestamps[approach][veh_class][movement].append(entry_time)
            self.last_actions[vid_path] = entry_time
            label = str(len(self.timestamps[approach][veh_class][movement]))
        print(msg)  # DEBUG
        return label, msg


    def update_vru_counts(self, vru_class, approach, erase_mode:bool, entry_time):
        key = f'vru_{vru_class}'
        msg=None
        entry_time = _format_time(entry_time)
        if erase_mode:
            if len(self.get_vru_counts(vru_class, approach)) > 0:
                deleted_entry = self.get_vru_counts(vru_class, approach).pop()
                msg = f'➖Erased a {approach}:[{vru_class}, VRU] entry @{deleted_entry}'
                try:
                    new_label = str(self.get_vru_counts(vru_class, approach)[-1])
                except IndexError:
                    new_label = '-'
            else:
                new_label = '-'
        else:
            self.timestamps[approach][key].append(entry_time)
            msg = f'➕Added a {approach}:[{vru_class}, VRU] entry @{entry_time}'
            new_label = str(len(self.get_vru_counts(vru_class, approach)))
        print(msg)
        return new_label, msg


    def save_file(self, path, cache=False):
        print(f"Saving file@ {path}")
        data = {
        'video_paths': self.config.video_paths,
        'date': self.config.date,
        'start_time':self.config.start_time,
        'last_actions': self.last_actions,
        'collection_type': self.config.collection_type,
        'approaches': self.config.approaches,
        'veh_classes':self.config.vehicle_classifications,
        'vru_classes':self.config.vru_classifications,
        'timestamps': self.timestamps
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        if cache:
            return '💾 Cache saved'
        else:
            try:
                os.remove('data/cache.json')
                print("--- found and deleted the cache")
            except FileNotFoundError:
                print("--- cache not found")
            return f'💾 data saved at {os.path.basename(path)}'



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