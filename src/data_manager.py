import json
import os

from src.intersection_config import IntersectionConfig


class DataManager:
    def __init__(self, config:IntersectionConfig, data_dict_params:tuple=None):
        self.config = config
        if config.timestamps:
            self.timestamps = config.timestamps
            self.last_actions = config.last_actions
        else:
            if config.collection_type == "Volume only":
                self.timestamps = _create_memory_volume(veh_classes=data_dict_params[0], vru_classes=data_dict_params[1],
                                                 movements=data_dict_params[2], approaches=self.config.approaches)
                self.last_actions = {path: 0.0 for path in config.video_paths}
            # elif config.collection_type == "Find Conflicts":

            # elif config.collection_type == "Near-Miss Evaluation":
            #     self.data

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


    def update_vru_counts(self, vru_class, approach, erase_mode:bool, entry_time_video):
        key = f'vru_{vru_class}'
        msg=None
        entry_time = _format_time(entry_time_video[0])
        vid_path = entry_time_video[1]
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
            self.last_actions[vid_path] = entry_time
            msg = f'➕Added a {approach}:[{vru_class}, VRU] entry @{entry_time}'
            new_label = str(len(self.get_vru_counts(vru_class, approach)))
        print(msg)
        return new_label, msg


    def save_file(self, path, cache=False, data=None):
        # data is used when collecting or evaluating conflicts.
        print(f"Saving file@ {path}")
        data = self._prepare_data(data)
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

    def _prepare_data(self, data):
        if self.config.collection_type=='Volume only':
            return  {
                'video_paths': self.config.video_paths,
                'date': self.config.date,
                'start_time': self.config.start_time,
                'last_actions': self.last_actions,
                'collection_type': self.config.collection_type,
                'approaches': self.config.approaches,
                'veh_classes': self.config.vehicle_classifications,
                'vru_classes': self.config.vru_classifications,
                'timestamps': self.timestamps
            }
        else:
            return {
                'video_paths': self.config.video_paths,
                'collection_type': self.config.collection_type,
                'timestamps': data
            }



def _create_memory_volume(veh_classes, vru_classes, movements, approaches):
    big_dict={}
    for approach in approaches:
        memory = {}
        for r in veh_classes:
            memory[r] = {c: [] for c in movements}
        for r in vru_classes:
            memory[f'vru_{r}'] = []
        big_dict[approach] = memory
    return big_dict

def _create_memory_conflict_detection(veh_classes, vru_classes, movements, approaches):
    #todo
    return

def _create_memory_conflict_evaluation(veh_classes, vru_classes, movements, approaches):
    #todo
    return


def _format_time(seconds):
    mins, secs = divmod(seconds, 60)
    formatted_time =  f'{int(mins):02d}:{secs:04.1f}'
    return formatted_time