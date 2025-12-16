import os
# ------------------ Load ENV Variables ------------------ #
import dotenv
# dotenv.load_dotenv()      -> Should Ideally be loaded via app.py

_cwd = os.path.abspath(os.getcwd())
STACK_DIR:str = os.getenv("stack_dir", r"Data\Session\Stack")
STACK_DIR = os.path.join(_cwd, STACK_DIR)
os.makedirs(STACK_DIR, exist_ok=True) # Makes directory if not present.
# -------------------------------------------------------- #

import pickle
import numpy as np
from Helpers import common_helpers
import shutil
from functools import lru_cache

class StackManager:
    """The stack manager maintains the stack for the session.
    ---
    1. It allows for capabilities for undo / redo and list of transformation histories.
    2. To reset the stack, simply remove the stack folder.
    
    :param canonical_npy: Contains the list of npy file names within the current edit session
    :type canonical_npy: list[str]
    :param parent_uuid: The uuid of the original uuid from /Data/Uploads
    :type parent_uuid: str
    :param current_pointer: The pointer location pointing to the current image
    :type current_pointer: int
    :param undoPossible: 
    :type undoPossible: boolean
    :param redoPossible:
    :type redoPossible: boolean
    :param currentImage: Returns the current Image np.ndarray read from disk
    :type currentImage: np.ndarray
    """
    def __init__(self):
        # os.makedirs ensures that the stack folder exists
        # If stack.pkl exists, previous session can be retrieved
        print("Initilising Stack Manager")
        
        self.stack_pkl = os.path.join(STACK_DIR, "stack.pkl")
        if os.path.exists(self.stack_pkl):
            print("Previous Session Found!")
            self.__retrieve_session()
        else:
            self.npy_stack:list[str] = []
            self.parent_uuid: str | None = None
            self.current_pointer = -1
            self.__png_cache: dict[int, bytes] = {}
        
        print(f"""Initialised Stack Manager\n
              \tImage Stack: {len(self.npy_stack)}
              \tParent UUID: {self.parent_uuid}
              \tPointer At : {self.current_pointer}
              """)
        
    def __retrieve_session(self):
        if not os.path.exists(self.stack_pkl):
            self.__init__()
            return
        
        """Reads directory to get previous session details"""
        # Already ensured by os.makedirs while loading env.
        with open(self.stack_pkl, 'rb') as prev:
            prev_session: StackManager = pickle.load(prev)
            
        # self.__dict__.update(prev_session.__dict__)
        
        self.npy_stack = prev_session.npy_stack
        self.current_pointer = prev_session.current_pointer
        self.parent_uuid = prev_session.parent_uuid
    
    def __save_session(self):
        """Over writes the stack file"""
        with open(self.stack_pkl, 'wb') as stack_file:
            pickle.dump(self, stack_file)

    def reset(self):
        """Resets the stack"""
        # Remove the directory and just make it again :)
        print("Resetting Stack")
        shutil.rmtree(STACK_DIR)
        os.makedirs(STACK_DIR, exist_ok=True)       
        self.__init__()       # Updates the stack vars
        # It is that simple :D
        
    def resetImage(self, npy_id: str):
        self.current_pointer = 0
        
        # Removes all other files from stack
        _removed_npy = self.npy_stack
        common_helpers.removeFiles(*_removed_npy, dir=STACK_DIR)
        
        self.npy_stack = [npy_id+".npy"]
        
        self.__save_session()
    
    def addImage(self, npy_id: str):
        """Adds Image after current image. All images in stack after current are removed"""
        
        # Move the pointer forward
        self.current_pointer += 1
        
        # # Get a new uuid -> Will be handled by the image operations
        # npy_id = common_helpers.generate_uuid()

        # # Save npy
        # npy_file = os.path.join(STACK_DIR, npy_id+".npy")
        # with open(npy_file, 'wb') as f:
        #     np.save(f, npy)

        # Removes all entries from stack after insert position
        _removed_npy = self.npy_stack[self.current_pointer:]
        common_helpers.removeFiles(*_removed_npy, dir=STACK_DIR)
        
        # Add entry to stack.
        self.npy_stack = self.npy_stack[:self.current_pointer]
        self.npy_stack.append(npy_id+".npy")
        
        # Should ideally always be true but explicit verifiction
        assert self.current_pointer == len(self.npy_stack) - 1
        
        self.__save_session()

    def undo(self) -> bool:
        if self.undoPossible:
            self.current_pointer -= 1
            self.__save_session()
            return True
        return False
    
    def redo(self) -> bool:
        if self.redoPossible:
            self.current_pointer += 1
            self.__save_session()
            return True
        return False
    
    @property
    def undoPossible(self) -> bool:
        return self.current_pointer > 0
    
    @property
    def redoPossible(self) -> bool:
        return self.current_pointer < len(self.npy_stack) -1
    
    def __conv_uint8(self, _npy):
        """Returns the npy in uint8"""
        if _npy.dtype == np.uint8:
            return _npy
        
        _min, _max = np.min(_npy), np.max(_npy)
        _range = _max - _min
        normalised_img = (_npy - _min) / _range
        range_mapped = np.uint8(normalised_img * 255)
        print("8 bit conversion of image", range_mapped.shape, range_mapped.dtype)
        return range_mapped
    
    # @lru_cache
    def getCurrentImage(self) -> bytes | None:
        """Returns the image for render"""
        
        if self.current_pointer <= -1:
            return None
        
        if self.current_pointer in self.__png_cache:
            return self.__png_cache[self.current_pointer]
        
        npy_file = self.npy_stack[self.current_pointer]
        npy_file = os.path.join(STACK_DIR, npy_file)
        with open(npy_file, 'rb') as f:
            npy = np.load(f)
        
        img8 = self.__conv_uint8(npy[:, :, :3])
        png_bytes = common_helpers.image_bytes(img8) # pyright: ignore[reportArgumentType]
        self.__png_cache[self.current_pointer] = png_bytes
        return png_bytes