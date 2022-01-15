
import sys
import shutil


if __name__ == '__main__':

    session_temp_root = sys.argv[1]

    # Remove the session temp root folder and all of its contents as the app closed and its
    # session is over ...
    shutil.rmtree(session_temp_root)

