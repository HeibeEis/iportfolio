import streamlit as st
import pandas as pd

from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from chat_openai import chat_with_openai

from gpt_response import fetch_gpt4_response

system_prompt = (""" 
    The Portfolio Optimiser GPT assists users in optimizing their insurance portfolios by providing insights into selecting insurance risks and strategic risk allocation. Tailored advice is offered based on the user’s stated risk appetites, if offered by the user. The Portfolio Optimiser analyzes and returns a table of risks that match the given appetite, strictly adhering to parameters. These may be Minimum Attachment, Maximum Limit, and Minimum Rate per Million (RPM), by industries etc.  

    The primary data source is the formatted accounts file. All tables and text responses will convert layer_limit_requested, attachment, and premium to US dollars, and total_commission to a percentage. The profit_center refers to the line of business, such as financial lines. Recognize that ‘k’ stands for thousands and automatically convert these inputs to their full numerical value for calculations and responses.  

    For class actions, the Portfolio Optimiser will utilize data from the Stanford SEC Database. The interaction style is formal, providing precise and professional responses. All data tables will be correctly formatted, with the last five columns formatted as follows: the first three columns (layer_limit_requested, attachment, and premium) will display the dollar sign and use accounting format, while the last two columns (total_commission and loss_ratio) will be presented as percentages.  

    When conducting analyses, the Portfolio Optimiser will return only the results without explaining the process or steps taken to arrive at the conclusion.  

    Ensure correct handling and access to user-uploaded files, and display tables as intended. When filtering, consider both lower and upper case variations of text inputs to ensure comprehensive results.  

    For custom reporting, the GPT will filter data based on user-defined criteria such as profit center, inception date range, expiry date range, currency, and premium thresholds. These reports can be exported in various formats including PDF, Excel, and CSV.  
"""  
)  

# Function for the table page 
def table_page():  
  # Display the custom title  
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
    # st.write(filtered_data)  
  else:  
      st.error("Dataframe is empty. Please go back to the previous page and upload a file.")  

  df = pd.DataFrame(filtered_data)
  gd = GridOptionsBuilder.from_dataframe(df)
  gd.configure_selection(selection_mode="multiple", use_checkbox=True)
  gridoptions = gd.build()

  grid_table = AgGrid(df, height=250, gridOptions=gridoptions, update_mode= GridUpdateMode.SELECTION_CHANGED)

  selected_row = grid_table["selected_rows"]

  selected_data = pd.DataFrame(selected_row)

  if selected_row is not None and not selected_row.empty:  
    # Layout: Left-bottom checkbox, right-bottom button  
    # col1, col2 = st.columns([1, 1])  
    # with col1:  
      apply_filters = st.checkbox("Apply Filters")  
    # with col2:  
      user_input = st.text_input("", value="", key="user_input")  
      if user_input.strip():  
        # Add the selected data to the messages before sending it to GPT-4  
          
          st.session_state.messages.append({"role": "user", "content": user_input})  
          if not selected_row.empty:  
            selected_data_json = selected_row.to_json(orient='records')  
            st.session_state.messages.append({"role": "system", "content": f"Here is the selected data in JSON format: {selected_data_json}"})  
          
          with st.spinner('Analyzing...'):  
              response = fetch_gpt4_response(st.session_state.messages)  
              if response:  
                  st.markdown(f"**You:** {user_input}")  
                  st.markdown(f"**Portfolio Optimizer:** {response}")  
                    
    # st.dataframe(selected_row)
    
    
      if apply_filters:  
        st.sidebar.header("Filter Options")  
        # Filter by Industry  
        industries = data['Industry'].unique()
        selected_industry = st.sidebar.multiselect('Select Industry', industries, default=None)