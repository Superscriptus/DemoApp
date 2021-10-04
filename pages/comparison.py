import streamlit as st
from .utilities import load_models


def page_code():

    comparison_data = {}

    for preset in ['A', 'B', 'C', 'D']:
        parameter_dict = st.session_state.config.simulation_presets[preset]

        comparison_data[preset] = load_models(
            project_count=parameter_dict['project_count'],
            dept_workload=parameter_dict['dept_workload'],
            budget_func=parameter_dict['budget_func'],
            train_load=parameter_dict['train_load'],
            skill_decay=parameter_dict['skill_decay'],
            rep=st.session_state.replicate,
            team_allocation=parameter_dict['team_allocation']
        )

    st.title("Comparison")

    st.write("This tab will allow comparison between two selected simulations.")
    option = st.multiselect(
        'Select team allocators:',
        ('Random',
         'Basic',
         'Niter0',
         'Basin',
         'Basin_w_flex'
         )
    )
    color = st.select_slider(
        'Select skill decay value:',
        options=[0.95, 0.99, 0.995]
    )
    st.image('images/projects_timeline_flex.png')

