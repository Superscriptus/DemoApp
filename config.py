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
                'preset_name': 'The Overcommitted Organization',
                'blurb': 'These organisations have committed too many staff to training, departmental workload and to '
                         'project work. As such, they do not have enough spare capacity (slack) to be able to choose '
                         'effective teams. Their project success rate and ROI suffer as a result.',
                'project_count': 10,
                'budget_func': True,
                'dept_workload': 0.3,
                'skill_decay': 0.95,
                'train_load': 0.3,
                'team_allocation': 'Flexible start time'
            },
            'B': {
                'preset_name': 'The Undercommitted Organization',
                'blurb': 'These organisations have too much slack and as a result they are not making '
                         'effective use of their workforce. They could afford to allocate more staff to project work '
                         'or introduce staff training for inactive workers.',
                'project_count': 1,
                'budget_func': True,
                'dept_workload': 0.1,
                'skill_decay': 0.95,
                'train_load': 0.0,
                'team_allocation': 'Flexible start time'
            },
            'C': {
                'preset_name': 'The Emergent Organization',
                'blurb': 'These organisations have achieved a balance between project work, staff training and '
                         'departmental workload. The emergent behaviour shows and orgnaisation that improves '
                         'over time.',
                'project_count': 3,
                'budget_func': True,
                'dept_workload': 0.1,
                'skill_decay': 0.995,
                'train_load': 0.1,
                'team_allocation': 'Flexible start time'
            },
            'D': {
                'preset_name': 'The Rigid Organization',
                'blurb': 'These organisations are too inflexible. They are burdened by departmental workload and do not'
                         ' train inactive staff. NOTE THAT BUDGET OFF MAKES THEM MORE FLEXIBLE.',
                'project_count': 2,
                'budget_func': False,
                'dept_workload': 0.3,
                'skill_decay': 0.95,
                'train_load': 0.0,
                'team_allocation': 'Flexible start time'
            }
        }

        self.default_simulation_parameters = {
            'project_count': 2,
            'budget_func': True,
            'dept_workload': 0.1,
            'skill_decay': 0.99,
            'train_load': 0.1
        }

    def __repr__(self):
        return (
            self.simulation_variables,
            self.simulation_presets,
            self.default_simulation_parameters
        )

