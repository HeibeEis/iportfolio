import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

# Initialize session state for page navigation and other input  
if 'page' not in st.session_state:  
    st.session_state.page = 'intro'  
if 'title' not in st.session_state:  
    st.session_state.title = ""  

def navigate_page(new_page):
  st.session_state.page = new_page

def init_input_page():
  st.title("Init Input")
  form = st.form(key="title_form")
  title_input = form.text_input("Portfolio Name", st.session_state.title)
  if title_input:  
    st.session_state.title = title_input
  dataset_option = form.selectbox('Select Business', ['Business1', 'Business2', 'Business3'], key='business')  
  column_option = form.selectbox('Select Products', ['Product1', 'Product2', 'Product3'], key='product')  

  # Use `form.form_submit_button` which we can control  
  submit_button = form.form_submit_button('next')

  if submit_button and title_input.strip():
    st.session_state.title = title_input 
    navigate_page(title_input)   
  elif submit_button: 
     st.error("Please type the title of next page.")

# Load the data into a DataFrame
def load_data():
  return pd.read_csv("Data1.csv")

# Function for the table page 
def table_page():  
  data = load_data()
  # Display the custom title  
  st.title(st.session_state.title)

  st.sidebar.header("Filter Options")

  # Filter by Client Country
  countries = data['client_country'].unique()
  selected_country = st.sidebar.multiselect("Select Client Country", countries, default=None)

  # Filter by Industry  
  industries = data['Industry'].unique()
  selected_industry = st.sidebar.multiselect('Select Industry', industries, default=None)

  # Filter by Currency  
  currencies = data['currency'].unique()
  selected_currency = st.sidebar.multiselect('Select Currency', currencies, default=None)

  # Apply filters to the DataFrame  
  filtered_data = data[  
      (data['client_country'].isin(selected_country)) &  
      (data['Industry'].isin(selected_industry)) &  
      (data['currency'].isin(selected_currency))  
  ]


  # Add custom CSS to extend the table size  
  st.markdown(  
   """  
   <style>  
   .dataframe-container {  
       width: 100%;  
       overflow: auto;  
   }  
   </style>  
   """,  
   unsafe_allow_html=True  
  )

  if len(filtered_data) == 0:  
    st.dataframe(data)  #'No data available with the current filters.'
  else:  
    st.subheader('Filtered Data')

    
    df = pd.DataFrame(filtered_data)
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_selection(selection_mode="multiple", use_checkbox=True)
    gridoptions = gd.build()

    grid_table = AgGrid(df, height=250, gridOptions=gridoptions, update_mode= GridUpdateMode.SELECTION_CHANGED)

    selected_row = grid_table["selected_rows"]

    selected_data = pd.DataFrame(selected_row)

    if selected_row is not None and not selected_row.empty:  
      st.subheader('Selected Data')
      
      apply_filters = st.checkbox("Apply filters")

      st.dataframe(selected_row)

       # Filter check button  
      
      
      filter_conditions = {}  

      if apply_filters:  
        st.sidebar.header("Filter Options")  
      

        # Specific columns to apply additional filters  
        filter_columns = ["attachment", "premium", "layer_limit_requested", "total_commission"]  
        
          # Sidebar filter options based on the selected data  
        for column in selected_data.columns:  
                if column == "favorite":  
                    continue  
                if selected_data[column].dtype == 'object':  
                    selected_values = st.sidebar.multiselect(f"Filter by {column}", options=selected_data[column].unique(), default=selected_data[column].unique())  
                    filter_conditions[column] = selected_values  
                elif np.issubdtype(selected_data[column].dtype, np.number) and column in ["attachment", "premium", "layer_limit_requested", "total_commission"]:  
                    min_val = selected_data[column].min()  
                    max_val = selected_data[column].max()  
                    selected_range = st.sidebar.slider(f"Filter by {column}", min_val, max_val, (min_val, max_val))  
                    filter_conditions[column] = selected_range 
        # Apply the filters to the selected data  
        for col, condition in filter_conditions.items():  
            if isinstance(condition, tuple):  
                selected_data = selected_data[(selected_data[col] >= condition[0]) & (selected_data[col] <= condition[1])]  

        st.subheader("Filtered Selected Data")  
        if selected_data.empty:  
            st.write("No data available with the current filters.")  
        else:  
            st.write(selected_data) 
  
    else: 
      st.write("")

# Page Navigation Logic  
if st.session_state.page == 'intro':  
    init_input_page()  
elif st.session_state.page == st.session_state.title:  
    table_page()  
