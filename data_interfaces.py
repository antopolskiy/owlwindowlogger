import logging
import pandas as pd

def get_json_data(path) -> list:
    import json
    json_data = []
    with open(path, 'r') as f:
        line = ' '
        while line != '':
            line = f.readline()
            try:
                json_data.append(json.loads(line))
            except json.JSONDecodeError as e:
                logging.error(e)
    return json_data


class Keys:
    _map = dict(MESSAGE="log_message",
                USER="user",
                HOST="hostname",
                TITLE="window_title",
                WIN_HANDLE="hwnd",
                PROCESS_NAME="process_name",
                PROCESS_ID="pid",
                IDLE="idle_seconds",
                TIME_START="start_timestamp",
                TIME_END="end_timestamp",
                TIME_LOG="log_timestamp")
    _revmap = {v: k for k, v in _map.items()}
    _datetime_keys = ("TIME_START", "TIME_END", "TIME_LOG")
    _datetime_format = "%Y-%m-%d %H:%M:%S.%f"

    @staticmethod
    def get(key):
        if key in Keys._map:
            return Keys._map[key]
        elif key in Keys._revmap:
            return Keys._revmap[key]
        else:
            logging.error(f"{key} in not found, None is returned.")
            return None

    @staticmethod
    def keys():
        return list(Keys._map.keys())

    @staticmethod
    def values():
        return list(Keys._map.values())

    @staticmethod
    def dt_keys():
        return Keys._datetime_keys

    @staticmethod
    def dt_format():
        return Keys._datetime_format


def parse_json_to_df(json_data) -> pd.DataFrame:
    columns = Keys.keys()
    df = pd.DataFrame(columns=columns)
    for (i, entry) in enumerate(json_data):
        for val in Keys.values():
            if val in entry:
                df.at[i, Keys.get(val)] = entry[val]
    return df


def parse_datetime(df, datetime_keys, strftime_format) -> pd.DataFrame:
    for key in datetime_keys:
        df[key] = pd.to_datetime(df[key], format=strftime_format)
    return df


def load_as_df(path) -> pd.DataFrame:
    json_data = get_json_data(path)
    df = parse_json_to_df(json_data)
    df = parse_datetime(df, Keys.dt_keys(), Keys.dt_format())
    return df
