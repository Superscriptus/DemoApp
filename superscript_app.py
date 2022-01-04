from application import Application
from pages import simulation, comparison, about
from streamlit import secrets
import json

app = Application()
app.create_page("About", about)
app.create_page("Simulation", simulation)
# app.create_page("Hypotheses", hypotheses)
app.create_page("Comparison", comparison)

with open(secrets["FIRESTORE_KEY_FILE"], "w") as ofile:
    json.dump(secrets["FIRESTORE"], ofile, indent=4)

app.execute()
