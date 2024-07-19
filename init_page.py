import streamlit as st
import pandas as pd

from io import StringIO

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
  col1, col2 = st.columns([1, 1])
  with col1:
    uploaded_file = form.file_uploader(
      "Upload Appetite Data Sheet", 
      accept_multiple_files=True, 
      
      help="Upload a CSV file containing your appetite data."
    )
  with col2:
    done_button = form.form_submit_button('Select Options')
  
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