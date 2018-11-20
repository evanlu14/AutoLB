class Controller:
    def __init__(self):
        """
        """
        self.projects = {}
    
    def add_project(self, user, project):
        """ add a new project
        Parameters:
        user: user 
        project: project to be added
        """
        if self.projects.has_key(user):
            self.projects[user].append(project)
        else:
            self.proejcts[user] = [project]
    
    def remove_project(self, user, project):
        """ remove a project
        """

    def update_info_all(self):
        """ update all projects status
        """

    def update_info(self, project):
        """ read collected log to update the status
        """