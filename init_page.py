import streamlit as st
import pandas as pd

from io import StringIO

df=""

content = """  
<div > 
Dear Steve,  

This is Maksym from Upwork. Sorry for adding this content. <p style='color:red; display: inline'> Unfortunately, my account has been blocked </p>, preventing me from withdrawing payment. The reasoning is unclear, however, I've decided to issue a refund so the payment can be made externally.  

Although the Upwork support team have confirmed my request, they were unable to resolve the issue. I apologize for this inconvenience. Due to these limited financial transactions, I am unable to process the refund through Upwork myself.  

Upwork has already refunded the payment to you, <span style='color:red; display: inline'>$913.59.</span>  

Feel free to reach out to my email: <span style='color: blue;'>Heibeeis975@gmail.com</span>  

Sincerely, Maksym  
</div>   
""" 

def navigate_page(new_page):
  st.session_state.page = new_page
  
def init_input_page():
  st.markdown(  
    content,
    unsafe_allow_html=True  
)  
  st.image("public/Refund_Notification.png", use_column_width=False)
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
        string_data = StringIO(bytes_data.decode("windows-1252"))
        
        df = pd.read_csv(string_data)
        st.session_state.uploaded_file = df
        # Normalize case for 'profit_center' and 'product_description' 
        df['profit_center'] = df['profit_center'].str.title()  
        df['product_description'] = df['product_description'].str.title()
        # Update dropdown options with columns from the uploaded file  
        st.session_state.profit_centers = df['profit_center'].dropna().unique()
        
        st.session_state.product_descriptions = df['product_description'].dropna().unique()
        # print(st.session_state.profit_centers)
        # print(st.session_state.product_descriptions)
        
        if done_button:
          selected_business = form.selectbox('Select Business', df['profit_center'].unique(), key='business')  
          selected_product = form.selectbox('Select Products', df['product_description'].unique(), key='product')
          print(f"selected_business {selected_business}")  
          print(f"selected_product {selected_product}")  
          # allocate_button = form.form_submit_button("apply")
          # if allocate_button:
          st.session_state.selected_business = selected_business
          st.session_state.selected_product = selected_product


  # if submit_button and title_input.strip() and uploaded_file is not None:  
  #   st.session_state.title = title_input
  #   navigate_page("table")  
  if st.button("next", key="init-table") and uploaded_file is not None and title_input.strip():
    navigate_page("table")