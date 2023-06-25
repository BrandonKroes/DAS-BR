import yaml


class YAMLParser:
    path = ""
    file = ""
    data = ""

    def __init__(self, path):
        self.path = path

    def serialize_to_dict(self):
        try:
            f = open(self.path, encoding='utf-8')
            self.data = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
        except FileNotFoundError:
            print(f"Tried to open file {self.path}, but unable to find the file.")
            exit(1)
        except IsADirectoryError:
            print(f'Directory given instead of a file {self.path}')
            exit(1)

    @staticmethod
    def DictToConfiguration(d):
        with open('../../config/conf.yml', 'w+') as outfile:
            yaml.dump(d, outfile, default_flow_style=False)

    @staticmethod
    def PathToDict(path):
        yp = YAMLParser(path)
        yp.serialize_to_dict()
        return yp.data
