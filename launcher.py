from pyopo import pyopo
import os


# __name__
if __name__=="__main__":
    drive_path = os.path.join(os.path.dirname(str(__file__)), "TESTDRIVE")
    executable_location = os.path.join(os.path.dirname(str(__file__)), "TESTDRIVE\M\APP\\\FAIRWAY.OPA")

    executable = pyopo.executable.load_executable(executable_location)

    # Set where the emulated file system is located
    executable.set_filesystem_path(drive_path)

    # Attach various debuggers
    executable.attach_dsf_debugger()
    executable.attach_profiler()

    executable.execute()