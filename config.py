"""
Configuration file for application.

Config is loaded and stored in the session state.

Contents:
    'simulation_variables' : definitions of coarse variables from model_vars data files, that are displayed
                             on the simulation page.
"""


class Config:

    def __init__(self):

        self.simulation_variables = {
            'ActiveProjects': 'Number of currently active projects.',
            'SuccessfulProjects': 'Number of successful projects that finished on this timestep.',
        }

    def __repr__(self):
        return self.simulation_variables

