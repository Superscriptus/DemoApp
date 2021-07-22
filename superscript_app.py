"""
TODO:
- plot simulation data from disk/memory
- change Stop to Play at end of simulation
- not that pickle is not robust to library version changes - consider migrating to alternative format.
- README.md (with instructions for MC)
- create notebook to generate static images
- implement live plotting from data (create data aggregation/pre-processing)
- read about secrets management
- issues with layout and SVG display...

Resources:
- simple multi-page: https://towardsdatascience.com/creating-multipage-applications-using-streamlit-efficiently-b58a58134030
- framework for multi-page apps: https://discuss.streamlit.io/t/multi-page-apps/266/15
- session variables...?
 """

from application import Application
from pages import hypotheses, simulation, comparison, about

app = Application()
app.create_page("About", about)
app.create_page("Simulation", simulation)
app.create_page("Hypotheses", hypotheses)
app.create_page("Comparison", comparison)
app.execute()

# col1, col2, col3 = st.beta_columns([1,5,1])
#
# with col1:
#     st.write("")
# with col2:
#     st.image('images/logo.png', use_column_width=True)#, width=400)
# with col3:
#     st.write("")
#

