from flask import request
import uuid, base64, os

def get_requestArgs(*args, check_all:bool=True):
    values = []
    for arg in args:
        param = request.args.get(arg)
        
        if check_all and param is None:
            # TODO, check if param is defined. Else throw error
            raise ValueError(f"Missing required param {arg}")
        
        values.append(param)
    
    return values

def generate_uuid() -> str:
    """
    Generates a URL-safe Base64-encoded UUID (22 characters long).
    """
    # 1. Generate a UUID (128-bit)
    random_uuid = uuid.uuid4()
    
    # 2. Get the 16-byte binary representation (digest)
    # This removes the hyphens and represents the full 128 bits
    uuid_bytes = random_uuid.bytes
    
    # 3. Encode the 16 bytes using URL-safe Base64
    # The URL-safe variant replaces '+' with '-' and '/' with '_'
    encoded_bytes = base64.urlsafe_b64encode(uuid_bytes)
    
    # 4. Convert to a string and strip the trailing padding ('==')
    # A 16-byte input results in 22 characters plus '==' padding,
    # which is redundant for file names.
    base64_uuid = encoded_bytes.decode('utf-8').rstrip('==')
    
    return base64_uuid.replace('-', '0')

def removeFile(path: str, dir=""):
    path = os.path.join(dir, path)
    if os.path.exists(path):
        os.remove(path)

def removeFiles(*files: str, dir=""):
    for file in files:
        removeFile(file, dir)


