import streamlit as st

from table_page import table_page
from init_page import init_input_page
from table_page import system_prompt

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
if 'user_input' not in st.session_state:  
    st.session_state.user_input = ""  
if 'messages' not in st.session_state:  
    st.session_state.messages = [
      {"role": "system", "content":system_prompt}
    ]  
if 'uploaded_file' not in st.session_state:  
    st.session_state.uploaded_file = None 
if 'chat_history' not in st.session_state:  
    st.session_state.chat_history = []  

def main():
  if st.session_state.page == 'intro':  
    init_input_page()  
  elif st.session_state.page == 'table':  
    table_page()  

if __name__ == "__main__":
  main()