





import os
from functools import cached_property
from dotenv import load_dotenv

load_dotenv()

#SUBMISSIONS_DIRPATH = "/content/drive/MyDrive/OpenAI TA Agent/submissions/Homework 4"
SUBMISSIONS_DIRPATH = os.getenv("SUBMISSIONS_DIRPATH")

class SubmissionsManager:

    def __init__(self, dirpath=SUBMISSIONS_DIRPATH, file_ext=".IPYNB"):
        self.dirpath = dirpath
        self.file_ext = file_ext

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


    #@cached_property
    #def starter_filepath(self):
    #    return self.find_filepath("STARTER")



if __name__ == "__main__":


    sm = SubmissionsManager()
    print(sm.dirpath)
    print(len(sm.filenames))

    starter_filepath = sm.find_filepath("STARTER")

    print(starter_filepath)
