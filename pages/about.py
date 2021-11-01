import streamlit as st


def page_code():
    st.title("About")

    col1, col2 = st.beta_columns([1, 9])
    col1.image('images/icon.png')
    col2.header("Welcome to SuperScript!")

    st.markdown(
        "Here you can explore our agent-based model of team formation. In this model, teams of workers are assigned to "
        "projects on each timestep using an algorithm that attempts to maximise the probability of project success. "
        "The properties of the organization emerge from the interactions of the workers, and evolve through time via a "
        "combination of mechanisms (for example: project work, training, skill decay). The skill level of individual "
        "workers is quantified by their 'Overall Rating' (OVR)."
    )

    st.write(
        "You can find the simulation code on [GitHub](https://github.com/Superscriptus/SuperScript) "
        "along with a "
        "[full specification]"
        "(https://github.com/Superscriptus/SuperScript/blob/master/documentation/model_specification.pdf)"
        " of the model.",
        unsafe_allow_html=True
    )

    st.subheader("Check out the following pages using the sidebar navigation:")
    # with st.beta_expander("Simulation"):

    st.subheader("Simulation")
    st.write("Explore the simulation in real-time and see how the output metrics vary over time. Select from "
             "pre-defined parameter presets or choose your own parameter values using the sidebar controls.")

    st.subheader("Comparison")
    st.write("Compare performance of the model across the five pre-selected parameter presets (A-E). Explore how the "
             "emergent properties of the organization vary according these different organizational strategies.")