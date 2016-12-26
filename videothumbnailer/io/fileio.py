from pathlib import Path

import yaml


class FileIo:
    def write_yaml(self, filenamewithoutextension, data):
        text = yaml.dump(data)
        with open(filenamewithoutextension + ".yml", "w") as f : f.write(text)

    def read_yaml(self, filenamewithoutextension):
        filename = filenamewithoutextension + ".yml"
        file = Path(filename)
        if not file.is_file():
            return None

        with open(filename, "r") as f : text = f.read()
        return yaml.safe_load(text)