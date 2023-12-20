





import os
from functools import cached_property
from dotenv import load_dotenv

load_dotenv()

#SUBMISSIONS_DIRPATH = "/content/drive/MyDrive/OpenAI TA Agent/submissions/Homework 4"
SUBMISSIONS_DIRPATH = os.getenv("SUBMISSIONS_DIRPATH")
STARTER_FILENAME = os.getenv("STARTER_FILENAME")

class SubmissionsManager:

    def __init__(self, dirpath=SUBMISSIONS_DIRPATH, file_ext=".IPYNB", starter_filename=STARTER_FILENAME):
        self.dirpath = dirpath
        self.file_ext = file_ext
        self.starter_filename = starter_filename

    @cached_property
    def filenames(self):
        return sorted([fn for fn in os.listdir(self.dirpath) if fn.upper().endswith(self.file_ext)])

    @cached_property
    def filepaths(self):
        return [os.path.join(self.dirpath, fn) for fn in self.filenames]

    def find_filepath(self, substr):
        for filepath in self.filepaths:
            if substr in filepath:
                return filepath
        return None


    @cached_property
    def starter_filepath(self):
        if self.starter_filename:
            return os.path.join(self.dirpath, self.starter_filename)
        #else:
        #    return self.find_filepath("STARTER")



if __name__ == "__main__":


    sm = SubmissionsManager()
    print("SUBMISSIONS DIRPATH:", sm.dirpath)
    print("FILES:", len(sm.filenames))
    print("STARTER DOC:", sm.starter_filepath)
