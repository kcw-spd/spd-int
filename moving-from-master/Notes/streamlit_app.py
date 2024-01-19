
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()
# Everything is accessible via the st.secrets dict:

st.write("DB username:", os.environ["db_username"])
st.write("DB password:", os.environ["db_password"])

# And the root-level secrets are also accessible as environment variables:

import os

st.write(
    "Has environment variables been set:",
    os.environ["db_username"] == os.environ["db_username"],
)
# Initialize connection.
conn = st.connection('mysql', type='sql', host='localhost',dialect='mysql', username=os.environ["db_username"], password=os.environ["db_password"], database='db')

# Perform query.
df = conn.query('SELECT * from inventory_table;', ttl=600)

# Print results.
for row in df.itertuples():
    st.write(f"{row.name} has a :{row.pet}:")