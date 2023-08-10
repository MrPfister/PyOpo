import os
import logging
import sys

import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)                                      


def translate_path_from_sibo(path: str, executable)->str:
    if path.lower().startswith("loc::"):
        path = path[5:]

    if len(path) > 2:
        # Could contain drive information
        if path[1] == ":":
            # Starts with drive prefix
            path = path[3:]
    elif len(path) == 0:
        return os.path.join(executable.drive_path, executable.current_drive, executable.current_path)

    if path[0] == "\\":
        # Remove rooted path
        path = path[1:]

    if "\\" not in path:
        # Just a pure file, append it to the current dir
        translated_d = os.path.join(executable.drive_path, executable.current_drive, executable.current_path, path)
    else:
        translated_d = os.path.join(executable.drive_path, executable.current_drive, path)

    return translated_d
    

def translate_path_to_sibo(path: str, executable, include_image=False)->str:
    translated_start_len = len(os.path.join(executable.drive_path, executable.current_drive))
        
    translated_d = os.path.join(executable.current_drive + ":", path[translated_start_len:])

    if include_image:
        translated_d = "LOC::" + translated_d

    return translated_d