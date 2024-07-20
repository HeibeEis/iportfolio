import streamlit as st
import pandas as pd

from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from gpt_response import fetch_gpt4_response

system_prompt = (""" 
    The Portfolio Optimiser GPT assists users in optimizing their insurance portfolios by providing insights into selecting insurance risks and strategic risk allocation. Tailored advice is offered based on the user’s stated risk appetites, if offered by the user. The Portfolio Optimiser analyzes and returns a table of risks that match the given appetite, strictly adhering to parameters. These may be Minimum Attachment, Maximum Limit, and Minimum Rate per Million (RPM), by industries etc.  

    The primary data source is the formatted accounts file. All tables and text responses will convert layer_limit_requested, attachment, and premium to US dollars, and total_commission to a percentage. The profit_center refers to the line of business, such as financial lines. Recognize that ‘k’ stands for thousands and automatically convert these inputs to their full numerical value for calculations and responses.  

    For class actions, the Portfolio Optimiser will utilize data from the Stanford SEC Database. The interaction style is formal, providing precise and professional responses. All data tables will be correctly formatted, with the last five columns formatted as follows: the first three columns (layer_limit_requested, attachment, and premium) will display the dollar sign and use accounting format, while the last two columns (total_commission and loss_ratio) will be presented as percentages.  

    When conducting analyses, the Portfolio Optimiser will return only the results without explaining the process or steps taken to arrive at the conclusion.  

    Ensure correct handling and access to user-uploaded files, and display tables as intended. When filtering, consider both lower and upper case variations of text inputs to ensure comprehensive results.  

    For custom reporting, the GPT will filter data based on user-defined criteria such as profit center, inception date range, expiry date range, currency, and premium thresholds. These reports can be exported in various formats including PDF, Excel, and CSV.  
    
    The primary data source is a formatted accounts file containing fields such as 'Industry', 'Layer Limit Requested', 'Attachment', 'Premium', 'Total Commission', 'Loss Ratio', and others. All monetary values (e.g., layer_limit_requested, attachment, premium) must be converted to US dollars. Percentages (e.g., total_commission, loss_ratio) must be formatted accordingly.  

    Return optimization result table for every data name.
    
    if users ask according to this type of requests : "Optimize my insurance portfolio based on the given risk appetite.", return table with this style : 
      Industry: Technology,
      Layer Limit Requested: $5,000,000,
      Attachment: $1,000,000,
      Premium: $200,000 
      Total Commission: 10%
      Loss Ratio: 30%
"""  
)  

# Custom CSS to fix the input box at the bottom  
st.markdown("""  
    <style>  
    input[id='user_input'] {  
        position: fixed;  
        right: 0;  
        bottom: 0 !important;  
        width: 100%;  
        background-color: inherit;  
        padding: 12px 8px;  
        box-shadow: 0px -1px 10px rgba(0, 0, 0, 0.1);  
        z-index: 3;  
    }  
    .main > div {  
        padding-bottom: 100px; /* Adjust padding to ensure content is above the input */  
    }  
    .stTextInput input {  
        width: 100%;  
    }  
    </style>  
    """, unsafe_allow_html=True) 

# The `st.empty` placeholder is used to keep track of where the input should be rendered  
input_placeholder = st.empty() 

# Template for the input HTML  
# text_input_html = """  
#     <div class="footer">  
#         <!-- The actual input field to take user text input -->  
#         <input id="user_input" type="text" style="width: 100%; padding: 10px; border-radius: 4px; border: 1px solid #ccc;" placeholder="Type your message here..."/>  
#     </div>  
#     <script>  
#         const input = document.getElementById("user_input");  
#         input.addEventListener("keydown", function(event) {  
#             if (event.key === "Enter") {  
#                 event.preventDefault();  
#                 const message = input.value;  
#                 input.value = "";  
#                 if (message !== "") {  
#                     window.parent.postMessage({ type: "streamlit:customEvent", data: message }, "*");  
#                 }  
#             }  
#         });  
#     </script>  
#     """  
# # Render the input HTML  
# input_placeholder.markdown(text_input_html, unsafe_allow_html=True)      
    

def preprocess_attachment(data):  
    # Remove '$' character and convert to numeric value  
    data['attachment'] = data['attachment'].replace({r'\$': '', 'k': 'e3', ",": "", "-": "", " ": ""}, regex=True).apply(pd.to_numeric)  
    data['layer_limit_requested'] = data['layer_limit_requested'].replace({r'\$': '', 'k': 'e3', ",": "", "-": "", " ": ""}, regex=True).apply(pd.to_numeric)  
    data['premium'] = data['premium'].replace({r'\$': '', 'k': 'e3', ",": "", "-": "", " ": ""}, regex=True).apply(pd.to_numeric)  
    return data

def show_table(data, set_check=True):
  df = pd.DataFrame(data)
  gd = GridOptionsBuilder.from_dataframe(df)
  gd.configure_selection(selection_mode="multiple", use_checkbox=set_check, header_checkbox=set_check)
  for col in df.columns:
    gd.configure_column(col, headerCheckboxSelection=set_check, checkboxSelection=set_check)
    break
  gridoptions = gd.build()
  grid_table = AgGrid(df, height=250, gridOptions=gridoptions, update_mode= GridUpdateMode.SELECTION_CHANGED)
  # Retrieve the selected row data  
  selected_rows = grid_table['selected_rows']  
  return selected_rows

# Function for the table page 
def table_page():  
  # Display the custom title  
  data = st.session_state.uploaded_file
  st.title(st.session_state.title)
  if data is not None:  
    selected_business = st.session_state.selected_business
    selected_product = st.session_state.selected_product
    
    filtered_data = data[(data['profit_center'] == selected_business) & (data['product_description'] == selected_product)]  
     # Filter options  
    st.sidebar.header("Filter Options")  
    
    # Filter by Industry  
    industries = data['Industry'].unique()  
    selected_industry = st.sidebar.multiselect('Select Industry', industries, default=None)  
    if selected_industry:  
        filtered_data = filtered_data[filtered_data['Industry'].isin(selected_industry)]  
        print(f"filter_data {filtered_data}")
    
    filtered_data = preprocess_attachment(filtered_data)
    
    attachment_min, attachment_max = filtered_data['attachment'].min(), filtered_data['attachment'].max()  
    layer_limit_min, layer_limit_max = filtered_data['layer_limit_requested'].min(), filtered_data['layer_limit_requested'].max()  
    premium_min, premium_max = filtered_data['premium'].min(), filtered_data['premium'].max()  
    
        
    # Slider filters  
    selected_attachment_range = st.sidebar.slider(  
        'Select Attachment Range',  
        min_value=int(attachment_min),  
        max_value=int(attachment_max),  
        value=(int(attachment_min), int(attachment_max)),  
        step=1  
    )  
    selected_layer_limit_range = st.sidebar.slider(  
        'Select Layer Limit Requested Range',  
        min_value=int(layer_limit_min),  
        max_value=int(layer_limit_max),  
        value=(int(layer_limit_min), int(layer_limit_max)),  
        step=1  
    )  
    selected_premium_range = st.sidebar.slider(  
        'Select Premium Range',  
        min_value=int(premium_min),  
        max_value=int(premium_max),  
        value=(int(premium_min), int(premium_max)),  
        step=1  
    )  

    # Apply slider filters  
    filtered_data = filtered_data[  
        (filtered_data['attachment'] >= selected_attachment_range[0]) &   
        (filtered_data['attachment'] <= selected_attachment_range[1]) &   
        (filtered_data['layer_limit_requested'] >= selected_layer_limit_range[0]) &   
        (filtered_data['layer_limit_requested'] <= selected_layer_limit_range[1]) &   
        (filtered_data['premium'] >= selected_premium_range[0]) &   
        (filtered_data['premium'] <= selected_premium_range[1])  
    ]  
    selected_row = show_table(filtered_data)  
    
  else:  
      st.error("Dataframe is empty. Please go back to the previous page and upload a file.")  
  

  if selected_row is not None and not selected_row.empty:  
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
                  st.session_state.messages.append({"role": "assistant", "content": response})  
                  # Store the history of inputs and responses  
                  st.session_state.chat_history.append({"user_input": user_input, "response": response})  
          # Displaying the entire chat history  
          for chat in st.session_state.chat_history:  
              st.markdown(f"**You:** {chat['user_input']}")  
              st.markdown(f"**iPortfolio:** {chat['response']}")         
      
   
    
      
