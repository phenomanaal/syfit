import pathlib
import json


class CountryCode:
    def __init__(self, json_filepath: str | None = None):

        if json_filepath is None:
            json_filepath = pathlib.Path(__file__).resolve().parent

        self.json_filepath = json_filepath
        self.names = json.load(open(json_filepath / "names.json"))
        self.phone = json.load(open(json_filepath / "phone.json"))

    def get_all_country_names(self):
        return list(self.names.values())

    def get_max_country_name_length(self):
        return max([len(n) for n in self.names.values()])

    def get_all_country_short_names(self):
        return list(self.names.items())

    def get_all_country_codes(self):
        return list(self.phone.values())

    def get_max_country_code_length(self):
        return max([len(n) for n in self.phone.values()])
