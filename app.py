import streamlit as st
import pandas as pd

# URL of the CSV file in your GitHub repository
csv_url = 'https://raw.githubusercontent.com/kennymcmillan/SportsTechX/master/sportstech.csv'

# Read the CSV file from the URL
df = pd.read_csv(csv_url)

# Display the data in Streamlit
st.title('SportsTechX Data')
st.write('This app displays the SportsTechX data from a CSV file stored in a GitHub repository.')

st.write('### Data')
st.dataframe(df)
