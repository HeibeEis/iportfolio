import os
import streamlit as st
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_gpt4_response(messages):  
    try:  
        response = openai.ChatCompletion.create(  
            model="gpt-4o",  
            messages=messages,  
            max_tokens=300,  
            temperature=0.7,  
        )  
        return response['choices'][0]['message']['content'].strip()  
    except Exception as e:  
        st.error(f"Error in fetching GPT-4 response: {e}")  
        return None  