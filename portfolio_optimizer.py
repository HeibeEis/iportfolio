import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO

from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state for page navigation and other input  
if 'page' not in st.session_state:  
    st.session_state.page = 'intro'  
if 'title' not in st.session_state:  
    st.session_state.title = ""  
if 'uploaded_file' not in st.session_state:  
    st.session_state.uploaded_file = None  
if 'profit_centers' not in st.session_state:  
    st.session_state.profit_centers = []  
if 'product_descriptions' not in st.session_state:  
    st.session_state.product_descriptions = []  
if 'selected_business' not in st.session_state:  
    st.session_state.selected_business = ""  
if 'selected_product' not in st.session_state:  
    st.session_state.selected_product = ""  
    
df=""

def navigate_page(new_page):
  st.session_state.page = new_page

def init_input_page():
  st.title("Init Input")
  form = st.form(key="title_form")

  # Title input
  title_input = form.text_input("Portfolio Name", st.session_state.title)

  if title_input:  
    st.session_state.title = title_input
  
  # File uploader  
  uploaded_file = form.file_uploader(
     "Upload Appetite Data Sheet", 
     accept_multiple_files=True, 
     
     help="Upload a CSV file containing your appetite data."
  )
  done_button = form.form_submit_button('done')
  
    # Process uploaded file and update dropdown options  
  if uploaded_file is not None:  
    st.session_state.uploaded_file = uploaded_file
    # Process different file formats  
    for file in uploaded_file:
      if file.name.endswith('.csv'):  
        bytes_data = file.getvalue()
        string_data = StringIO(bytes_data.decode("utf-8"))
        
        df = pd.read_csv(string_data)
        st.session_state.uploaded_file = df
        # Update dropdown options with columns from the uploaded file  
        st.session_state.profit_centers = df['profit_center'].dropna().unique()
        st.session_state.product_descriptions = df['product_description'].dropna().unique()
        # print(st.session_state.profit_centers)
        # print(st.session_state.product_descriptions)
        
        if done_button:
          selected_business = form.selectbox('Select Business', df['profit_center'].unique(), key='business')  
          selected_product = form.selectbox('Select Products', df['product_description'].unique(), key='product')  
          st.session_state.selected_business = selected_business
          st.session_state.selected_product = selected_product

  
  # if submit_button and title_input.strip() and uploaded_file is not None:  
  #   st.session_state.title = title_input
  #   navigate_page("table")  
  if st.button("next"):
    navigate_page("table")

# Function for the table page 
def table_page():  
  data = st.session_state.uploaded_file
  st.title(st.session_state.title)
  if data is not None:  
    # print(selected_business)
    # print(selected_product)
    selected_business = st.session_state.selected_business
    selected_product = st.session_state.selected_product
    print(selected_business)
    # print(data[data['profit_center'] == selected_business])
    filtered_data = data[(data['profit_center'] == selected_business) & (data['product_description'] == selected_product)]  
    st.write(filtered_data)  
  else:  
      st.error("Dataframe is empty. Please go back to the previous page and upload a file.")  

if st.session_state.page == 'intro':  
    init_input_page()  
elif st.session_state.page == 'table':  
    table_page()  
