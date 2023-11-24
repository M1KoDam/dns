import json
import datetime


def format_key(domain_name, a_type):
    return f"{domain_name}|{a_type}"


def filter_cache_values(value):
    result = []
    for item in value:
        a_class, addr, tll, data_length, creation_time = item
        now = datetime.datetime.now()
        new_tll = int((creation_time - now + datetime.timedelta(seconds=tll)).total_seconds())
        if new_tll > 0:
            result.append([a_class, addr, new_tll, data_length, creation_time])
    return result


class DNSAnswersCache:
    def __init__(self):
        self.cache_path = "DNS/Data/answers.json"
        self.cache = self.__load_answers_from_json()

    def write_answers_to_cache(self, domain_name, a_type, cache: list):
        now = datetime.datetime.now()
        self.cache[format_key(domain_name, a_type)] = [(*item, now) for item in cache]
        self.__write_answers_to_json()

    def load_answers_from_cache(self, domain_name: str, a_type: str) -> list:
        if format_key(domain_name, a_type) in self.cache.keys():
            loaded = self.cache[format_key(domain_name, a_type)]
            result = filter_cache_values(loaded)
            return result
        return []

    def __load_answers_from_json(self) -> dict:
        try:
            with open(self.cache_path, "r", encoding='utf-8') as read_file:
                file_data = read_file.read()
                if file_data.strip() != "":
                    return json.loads(file_data, object_hook=datetime_hook)
        except:
            with open(self.cache_path, "w", encoding='utf-8'):
                pass
        return {}

    def __write_answers_to_json(self):
        write_cache = {}
        with open(self.cache_path, "w", encoding='utf-8') as write_file:
            for key, value in self.cache.items():
                result = filter_cache_values(value)
                if len(result) > 0:
                    write_cache[key] = result

            json.dump(write_cache, write_file, ensure_ascii=False, default=datetime_handler)


def datetime_handler(obj):
    if isinstance(obj, datetime.datetime):
        return {
            "__type__": "datetime",
            "isoformat": obj.isoformat()
        }
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def datetime_hook(obj):
    if "__type__" in obj and obj["__type__"] == "datetime":
        return datetime.datetime.fromisoformat(obj["isoformat"])
    return obj
