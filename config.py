"""
Configuration file for application.

Config is loaded and stored in the session state.

Contents:
    'simulation_variables' : definitions of coarse variables from model_vars data.bak files, that are displayed
                             on the simulation page.
"""


class Config:

    def __init__(self):

        self.simulation_variables = {
            'ActiveProjects': 'Number of currently active projects.',
            'SuccessfulProjects': 'Number of successful projects that finished on this timestep.',
            'FailedProjects': 'Number of failed projects that finished on this timestep.',
            'NullProjects': 'Number of null (un-staffed) projects that finished on this timestep.',
            'WorkersOnProjects': 'Number of workers engaged in project work on this timestep.',
            'WorkersWithoutProjects': 'Number of workers not engaged in project work on this timestep. '
                                      '(May be engaged in departmental work.)',
            'WorkersOnTraining': 'Number of workers engaged in training on this timestep.',
            'ProjectLoad': 'Fraction of total capacity engaged in project work on this timestep.',
            'TrainingLoad': 'Fraction of total capacity engaged in training on this timestep.',
            'DeptLoad': 'Fraction of total capacity engaged in departmental work.',
            'Slack': 'Fraction of total capacity not engaged in projects, training or departmental work.',
            'AverageWorkerOVR': 'Mean worker overall rating (OVR) across workforce.',
            'AverageTeamOVR': 'Mean team overall rating (OVR) across all teams currently engaged in project work.',
            'AverageSuccessProbability': 'Mean probability of success across currently active projects.',
            'RecentSuccessRate': 'Fraction of projects that were successful over previous XX timesteps.',
            'WorkerTurnover': 'Number of workers replaced due to inactivity on this timestep.',
            'ProjectsPerWorker': 'Mean number of projects that a worker is engaged in, across the workforce.',
            'AverageTeamSize': 'Mean number of workers in a team, across active projects.'
        }

        self.simulation_presets = {
            'A': {
                'project_count': 10,
                'budget_func': True
            },
            'B': {
                'project_count': 1,
                'budget_func': True
            }
        }

    def __repr__(self):
        return self.simulation_variables

