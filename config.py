"""
Configuration file for application.

Config is loaded and stored in the session state.

Contents:
    'simulation_variables' : definitions of coarse variables from model_vars data.bak files, that are displayed
                             on the simulation page.
"""


class Config:

    def __init__(self):

        self.config_params = {
            'max_replicates': 1 #5
        }

        self.simulation_variables = {
            'Roi': 'Return on investment as %.',
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
                'blurb': 'These organizations have committed too many staff to training, departmental workload and to '
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
                'blurb': 'These organizations have too much slack and as a result they are not making '
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
                'blurb': 'These organizations have achieved a balance between project work, staff training and '
                         'departmental workload. The emergent behaviour shows an organization that improves '
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
                'blurb': 'These organizations are too inflexible. They are burdened by departmental workload and do not'
                         ' train inactive staff. Project teams are allocated at random.',
                'project_count': 2,
                'budget_func': True,
                'dept_workload': 0.3,
                'skill_decay': 0.95,
                'train_load': 0.0,
                'team_allocation': 'Random'
            },
            'E': {
                'preset_name': 'The Adaptive Organization',
                'blurb': 'This organizations has the same parameters as C: The Emergent Organization, but uses a '
                         'flexible workforce with reduced slack. Instead workers are hired from an external pool as'
                         'and when they are needed for project work.',
                'project_count': 3,
                'budget_func': True,
                'dept_workload': 0.1,
                'skill_decay': 0.995,
                'train_load': 0.1,
                'team_allocation': 'Flexible start time'
            }
        }

        self.default_simulation_parameters = {
            'project_count': 10,
            'budget_func': True,
            'dept_workload': 0.3,
            'skill_decay': 0.95,
            'train_load': 0.3,
            'team_allocation': 'Flexible start time'
        }

        self.simulation_plots = {
            'Return on Investment (ROI)': {
                'column_names': ['Roi'],
                'column_colours': ['blue'],
                'y_label': 'ROI (%)',
                'info': 'Return on investment as a %.'
            },
            'Active Project Count': {
                'column_names': ['ActiveProjects'],
                'column_colours': ['blue'],
                'y_label': 'Number of projects',
                'info': 'The number of projects that are currently running.'
            },
            'Project Plot': {
                'column_names': ['SuccessfulProjects', 'FailedProjects', 'NullProjects'],
                'column_colours': ['green', 'red', 'orange'],
                'y_label': 'Number of projects',
                'info': 'The number of successful, failed and null projects that finish on a each timestep. (Null '
                        'projects are those to which a team could not be assigned.)'
            },
            'Worker Plot': {
                'column_names': ['WorkersOnProjects', 'WorkersWithoutProjects', 'WorkersOnTraining'],
                'column_colours': ['green', 'red', 'orange'],
                'y_label': 'Number of workers',
                'info': 'The number of workers on projects, without projects and on training on a each timestep.'
            },
            'Load Plot': {
                'column_names': ['ProjectLoad', 'TrainingLoad', 'DeptLoad', 'Slack'],
                'column_colours': ['green', 'orange', 'red', 'blue'],
                'y_label': 'Fraction of capacity',
                'info': 'Workforce activity by fraction of total capacity.'
            },
            'OVR Plot': {
                'column_names': ['AverageWorkerOvr', 'AverageTeamOvr'],
                'column_colours': ['green', 'blue'],
                'y_label': 'OVR',
                'info': 'Overall Rating (OVR) values for workers and teams. OVR is a measure of skill level across the '
                        'five hard skills.'
            },
            'Success Plot': {
                'column_names': ['RecentSuccessRate', 'AverageSuccessProbability'],
                'column_colours': ['green', 'blue'],
                'y_label': 'Rate ; Probability',
                'info': 'Recent project success rate and current average success probability for active teams.'
            },
            'Turnover Plot': {
                'column_names': ['WorkerTurnover', 'ProjectsPerWorker', 'AverageTeamSize'],
                'column_colours': ['red', 'green', 'blue'],
                'y_label': 'Count',
                'info': 'Worker turnover: number of workers replaced due to inactivity.  \n'
                        'Projects per worker: mean number of projects that each worker contributes to.  \n'
                        'Average team size: mean number of workers per team.'
            },
        }

    def __repr__(self):
        return (
            self.simulation_variables,
            self.simulation_presets,
            self.default_simulation_parameters
        )

