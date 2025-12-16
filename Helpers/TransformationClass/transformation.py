import time

class Transformation:
    def __init__(self, operation: str, input_id: str, params: dict):
        self.operation = operation
        self.input_id = input_id
        self.params = params
        self.time = time.ctime(time.time())

    def __repr__(self):
        out_str = f"""Tranformation performed:{{
            "Operation": {self.operation},
            "Input File ID": {self.input_id},
            "Parameters": {self.params},
            "Time": {self.time}
        }}"""
        
        return out_str