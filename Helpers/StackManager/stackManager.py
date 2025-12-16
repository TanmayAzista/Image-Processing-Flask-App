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
        self.stack_pkl = os.path.join(STACK_DIR, "stack.pkl")

        if os.path.exists(self.stack_pkl):
            self.__retrieve_session()
        else:
            self.npy_stack:list[str] = []
            self.parent_uuid: str | None = None
            self.current_pointer = -1
        pass
    
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
        shutil.rmtree(STACK_DIR)
        os.makedirs(STACK_DIR, exist_ok=True)       
        self.__init__()       # Updates the stack vars
        # It is that simple :D
        
    def addImage(self, npy):
        """Adds Image after current image. All images in stack after current are removed"""
        # Move the pointer forward
        self.current_pointer += 1
        
        # Get a new uuid
        npy_id = common_helpers.generate_uuid()

        # Save npy
        npy_file = os.path.join(STACK_DIR, npy_id+".npy")
        with open(npy_file, 'wb') as f:
            np.save(f, npy)

        # Removes all entries from stack after insert position
        _removed_npy = self.npy_stack[self.current_pointer:]
        common_helpers.removeFiles(*_removed_npy, dir=STACK_DIR)
        
        # Add entry to stack.
        self.npy_stack = self.npy_stack[:self.current_pointer]
        self.npy_stack.append(npy_id+".npy")
        
        # Should ideally always be true but explicit verifiction
        assert self.current_pointer == len(self.npy_stack) - 1
        
        self.__save_session()

    def undo(self):
        if self.undoPossible:
            self.current_pointer -= 1
            self.__save_session()
    
    def redo(self):
        if self.redoPossible:
            self.current_pointer += 1
            self.__save_session()
    
    @property
    def undoPossible(self) -> bool:
        return self.current_pointer > 0
    
    @property
    def redoPossible(self) -> bool:
        return self.current_pointer < len(self.npy_stack) -1
    
    def getCurrentImage(self) -> np.ndarray | None:
        """Returns the file"""
        npy_file = None
        
        if self.current_pointer <= -1:
            return None
        
        npy_file = self.npy_stack[self.current_pointer]
        npy_file = os.path.join(STACK_DIR, npy_file)
        with open(npy_file, 'rb') as f:
            return np.load(f)