"""
TODO:
- plot simulation data.bak from disk/memory
- change Stop to Play at end of simulation
- not that pickle is not robust to library version changes - consider migrating to alternative format.
- README.md (with instructions for MC)
- create notebook to generate static images
- implement live plotting from data.bak (create data.bak aggregation/pre-processing)
- read about secrets management
- issues with layout and SVG display...

Resources:
- simple multi-page: https://towardsdatascience.com/creating-multipage-applications-using-streamlit-efficiently-b58a58134030
- framework for multi-page apps: https://discuss.streamlit.io/t/multi-page-apps/266/15
- session variables...?
 """
from application import Application
from pages import simulation, comparison, about
from streamlit import secrets
import streamlit_analytics
import tempfile
import json

app = Application()
app.create_page("About", about)
app.create_page("Simulation", simulation)
# app.create_page("Hypotheses", hypotheses)
app.create_page("Comparison", comparison)

with open(secrets["FIRESTORE_KEY_FILE"], "w") as ofile:
    json.dump(secrets["FIRESTORE"], ofile, indent=4)

with streamlit_analytics.track(
    unsafe_password=secrets["ANALYTICS_PASSWORD"],
    firestore_key_file=secrets["FIRESTORE_KEY_FILE"],
    firestore_collection_name=secrets["FIRESTORE_COLLECTION"]
):
    app.execute()
