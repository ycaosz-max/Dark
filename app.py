import streamlit as st

# Initialize session state for api_key if not already present
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

# Function to update session state api_key
def update_api_key(api_input):
    st.session_state.api_key = api_input

# Check for user input and button click
api_input = st.text_input('Enter your API key:')
if st.button('Submit'):
    update_api_key(api_input)

# Synchronize API key handling
if st.session_state.api_key:
    api_key = st.session_state.api_key
else:
    api_key = st.secrets.get('SILICONFLOW_API_KEY', '')

# Use the api_key for your application logic
st.write('Using API key:', api_key)