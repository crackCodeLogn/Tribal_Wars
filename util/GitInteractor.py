"""
@author Vivek
@since 29/08/20
"""


class GitInteractor:
    def __init__(self, file_source):
        self.file_source = file_source

    def commit(self, file, commit_msg):
        self.__add(file)

        print("Commit done!")

    def push(self):
        print("Git push complete!")

    def __add(self, file):
        print("File added to Git!")

    def pull(self):
        print("Git pull complete")
