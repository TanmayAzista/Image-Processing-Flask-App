import time

class Transformation:
    def __init__(self, operation: str, input_npy_id: str, params: dict):
        self.operation = operation
        self.input_npy_id = input_npy_id
        self.params = params
        self.time = time.ctime(time.time())

    def __repr__(self):
        out_str = f"""Tranformation performed:{{
            "Operation": {self.operation},
            "Input File ID": {self.input_npy_id},
            "Parameters": {self.params},
            "Time": {self.time}
        }}"""
        
        return out_str
    
class TransformatioManager:
    def __init__(self):
        pass