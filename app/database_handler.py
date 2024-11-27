class DatabaseHandler:
    def __init__(self, file_path="app/data/merchantdb"):
        self.file_path = file_path

    def save_data(self, data):
        with open(self.file_path, "w") as file:
            for key, value in data.items():
                file.write(f"{key}={value}\n")

    def load_data(self):
        try:
            with open(self.file_path, "r") as file:
                data = {}
                for line in file:
                    key, value = line.strip().split("=", 1)
                    data[key] = value
                return data
        except FileNotFoundError:
            return {}
