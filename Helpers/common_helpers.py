from flask import request
import typing as T

def get_requestArgs(*args, check_all:bool=True):
    values = []
    for arg in args:
        param = request.args.get(arg)
        
        if check_all and param is None:
            # TODO, check if param is defined. Else throw error
            raise ValueError(f"Missing required param {arg}")
        
        values.append(param)
    
    return values