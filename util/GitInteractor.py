"""
@author Vivek
@since 29/08/20
"""
import json
import os

from util.Helper import read_generic_config


class GitInteractor:
    def __init__(self, file_source):
        self.file_source = file_source

    def commit(self, file, commit_msg):
        self.__add(file)
        git_details = json.loads(open(self.file_source).read())

        comm = "git commit --author='{name} <{email}>' -m '{msg}'".format(
            name=read_generic_config(git_details, 'author'),
            email=read_generic_config(git_details, 'email'),
            msg=commit_msg
        )
        self.exec(comm)
        print("Commit done!")

    def push(self):
        self.exec("git push")
        print("Git push complete!")

    def __add(self, file):
        comm = "git add {}".format(file)
        self.exec(comm)
        print("File added to Git!")

    def pull(self):
        print("Git pull complete")

    def exec(self, comm):
        print("Executing => " + comm)
        os.system(comm)


if __name__ == '__main__':
    base_working_dir = os.path.dirname(os.path.realpath(__file__)) + "/../"
    config = json.loads(open(base_working_dir + 'res/config.json').read())

    if config['git']['enabled']:
        code_mode = 'p'
        world = 9
        delta_addition = 0
        delta_removal = 0

        git_interactor = GitInteractor(config['git']['path'])
        git_commit_msg = "Modifying world en{code_mode}{world} in +{delta_addition} {delta_removal} barbs".format(
            code_mode=code_mode, world=world,
            delta_addition=delta_addition, delta_removal=delta_removal)
        git_interactor.commit('{}/en{}{}/{}.json'.format(base_working_dir, code_mode, world, 'local_config'), commit_msg=git_commit_msg)
        git_interactor.push()
