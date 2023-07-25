import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import re
sys.path.append(os.path.join(os.getcwd(),"src"))
# sys.path.append("..\src")
from summary_functions import  *
from data_extract import *
import streamlit.components.v1 as components
import json
from streamlit_functions import *
from google.oauth2 import service_account
import gspread

# For logging feedback and search in google sheets
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

# Font options for selection in timeline
FONT_DICT = {
    "Arial": "Arial, sans-serif",
    "Helvetica": "Helvetica, sans-serif",
    "Times New Roman": "Times New Roman, serif",
    "Georgia": "Georgia, serif",
    "Courier New": "Courier New, monospace",
    "Verdana": "Verdana, sans-serif",
    "Trebuchet MS": "Trebuchet MS, sans-serif",
    "Arial Black": "Arial Black, sans-serif",
    "Impact": "Impact, sans-serif",
    "Comic Sans MS": "Comic Sans MS, sans-serif",
    "Palatino": "Palatino, serif",
    "Garamond": "Garamond, serif",
    "Bookman": "Bookman, serif",
    "Arial Narrow": "Arial Narrow, sans-serif",
    "Lucida Console": "Lucida Console, monospace"
}
REVERSE_FONT_DICT = {value:key for key,value in FONT_DICT.items()}
FONT_LIST = tuple(FONT_DICT.keys())

#Read about section
with open(os.path.join(DATA_PATH,'about.txt')) as about:
    about_str = about.read()

#Set page configs for streamlit app
st.set_page_config(page_title="Timeline Generator",
    page_icon="⏳",
    layout="wide",
    menu_items={
        'About': about_str
    })


# Create a connection object for connecting with google sheets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
client = gspread.authorize(credentials)
workbook = client.open("timelineGen")

#sheets in the google workbook
feedback_sheet = workbook.worksheet('feedback')
gpt_sheet = workbook.worksheet('gpt')

# global variables for different folder paths
DATA_PATH = os.path.join(os.getcwd(),'data')
APP_PATH = os.getcwd()
MAX_TEXT_CHARS = 16000

#config dictionary for table display
SUMMARY_COLUMN_CONFIG ={
        "Event" : st.column_config.TextColumn(
            "Event",
            width="large",
            default = "None"
        ),
    "Date" : st.column_config.TextColumn(
        "Date",
        default = "None"
    ),
    "Order": st.column_config.NumberColumn(
            "Order",
            help="Order of the event in timeline",
            min_value=1,
            step=1,
            default = 1,
        ),
    "Select": st.column_config.CheckboxColumn(
            "Select",
            help="Select the events you wish to see in timeline plot",
            default=True
        )
    }

content_moderation_error = True
#initialising session_states when the app first runs
if 'update_summary_key' not in st.session_state:
    st.session_state['update_summary_key'] = False

if 'update_timeline_key' not in st.session_state:
    st.session_state['update_timeline_key'] = False

if 'first_timeline_key' not in st.session_state:
    st.session_state['first_timeline_key'] = True

if 'download_timeline_png_key' not in st.session_state:
    st.session_state['download_timeline_png_key'] = True

if 'chatgpt_tokens' not in st.session_state:
    st.session_state['chatgpt_tokens'] = 0

if 'timeline_format_key' not in st.session_state:
    st.session_state['timeline_format_key'] = {
                                                'circle_color':'#7DB46C',
                                                'middle_line_color':'#010101',
                                                'text_box_color':'#ABD6DF',
                                                'background_color':'#E7EBE0',
                                                'font_html': "Arial, sans-serif"
                                            }

# Website header
st.title('Generate a TimeLine! ⏳')

#sidebar with the about section
with st.sidebar:
    st.markdown(about_str)

#topic/url input textbox
topic = st.text_input(label = "Enter a Topic or URL", max_chars = 100,\
                      help = "Enter a topic for which you need to generate a timeline.")

#expander to add custom text
with st.expander("Or add your own text"):
    topic_text = st.text_area(label = "topic_text",label_visibility = "collapsed", max_chars = 24000, height = 400)

#enter button to start timeline generation
enter_button = st.button("Generate Timeline!")

#the following sequence functions are run once enter_button is clicked i.e. enter_button is true.
if enter_button:
    with st.spinner('Generating Timeline. It may take a while ...'):
        
        if len(topic)>0 & len(topic_text) > 0:
            st.warning('As both the topic and user defined text are populated, we use "Enter Topic" text input to fetch topic data and generate the timeline. If you need to use user defined text, delete the text in "Enter Topic" text box ', icon="⚠️")

        #get summary of the topic if a topic is entered else use the custom text the user has input
        if len(topic) > 0:
            #get the summary table along with the source URL and gpt usage data
            summary,source,gpt_metadata = get_summary(topic) 
        else:
            summary,gpt_metadata = get_summary_from_text(topic_text)
            source = "User Text"
            
            # save the first word of the user input text to append to the timeline and csv files to be downloaded.
            topic = topic_text.split(" ",1)[0]
            #remove any characters other than alphabets to make sure the name does not violate any file_name conventions.
            topic = re.sub(r"[^a-zA-Z]", "", topic)

        if summary is None:
            st.error(f'''The input text failed content moderation guidelines by OpenAI,
            please recheck your text, Text Source : `{source}`''', icon="🚨")
            content_moderation_error = False
        else:
                
            #save gpt usage data in google sheets. chatgpt_tokens are saved seperately.
            gpt_sheet.insert_row(['t_'+topic]+gpt_metadata + [st.session_state['chatgpt_tokens']],2)
            st.session_state['chatgpt_tokens'] = 0
    
            #add select column to summary and update all session states.
            summary['Select'] = True
            st.session_state['source_key'] = source
            st.session_state['topic_key'] = topic
            st.session_state['update_summary_key'] = True
            st.session_state['summary_key'] = summary

if (st.session_state['update_summary_key'] or enter_button) and content_moderation_error:
    left_container, right_container = st.columns(2)
    summary = st.session_state['summary_key']
    st.session_state['update_summary_key'] = True

    with left_container:
        st.write("##### Timeline Data")

        form_data_editor = st.form("data_editor")

        with form_data_editor:
            data_editor_help = st.container()
            with data_editor_help:
                st.caption(f"Source : {st.session_state['source_key']}")
                st.caption("You can delete, change content of the cells and select/deselect the events in the table below. Click on Update Timeline! to reflect the changes in the timeline.")
                
            # with left_right_container:
            update_timeline_button = st.form_submit_button("Update Timeline!",\
                                               help = 'Edit the DataFrame and Click on "Update Timeline" to reflect the changes')

        if enter_button:
            generate_json(summary)
            st.session_state['first_timeline_key'] = False
            
        if update_timeline_button:
            if 'data_editor' in st.session_state:
                data_editor = st.session_state['data_editor']
                edited_rows = data_editor['edited_rows']
                for i,edits in edited_rows.items():
                    for col,val in edits.items():
                        summary.loc[i,col] = val
                        
                summary.reset_index(inplace = True,drop = True)
                deleted_rows = [i for i in data_editor['deleted_rows'] if i in summary.index]
                summary = summary.drop(deleted_rows,axis = 0)
                data_editor['deleted_rows'] = []
                added_rows = data_editor['added_rows']
                if len(added_rows) > 0:
                    
                    added_rows_df = pd.DataFrame(added_rows)
                    summary = pd.concat([summary,added_rows_df],ignore_index=True)
                    summary = summary.reset_index(drop = True)
                    data_editor['added_rows'] = []
                    
                summary = summary.sort_values('Order')
                print(st.session_state['data_editor'])
                st.session_state['summary_key'] = summary
                display_summary = summary[summary.Select]
                generate_json(display_summary)

        download_summary(summary,st.session_state['topic_key'])
                
    with right_container:
        with st.expander("Format Timeline"):
            format_timeline = st.form('format_timeline',clear_on_submit = False)
                                     
            with format_timeline:
                color_columns = st.columns(4)
                
                circle_color = color_columns[0].color_picker('Circle', '#7DB46C')
                middle_line_color = color_columns[1].color_picker('Vertical Line', '#010101')
                text_box_color = color_columns[2].color_picker('Text Box', '#ABD6DF')
                background_color = color_columns[3].color_picker('Background', '#E7EBE0')
                font = st.selectbox('Text Font',FONT_LIST,index = 0)
                font_html = FONT_DICT[font]
                format_timeline_submit = st.form_submit_button('Apply')

                if format_timeline_submit:
                    st.session_state['timeline_format_key'] = {
                                            'circle_color':circle_color,
                                            'middle_line_color':middle_line_color,
                                            'text_box_color':text_box_color,
                                            'background_color':background_color,
                                            'font_html':font_html
                                        }
                    
        html_string = get_timeline_html(st.session_state['topic_key'],st.session_state['timeline_format_key'],\
                                        st.session_state['download_timeline_png_key'])
        
        components.html(html_string,scrolling = True,height = 550)
        download_timeline() 
            
    summary = form_data_editor\
    .data_editor(summary[['Order','Date','Event','Select']],num_rows="dynamic",use_container_width=True,\
                                key = 'data_editor',height = 400,\
                                column_config = SUMMARY_COLUMN_CONFIG, hide_index = True)

st.markdown(
        """
        <style>
        .streamlit-expanderHeader p {
            font-size: 15px;
            font-weight: 600;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )

with st.expander("Feedback Form"):
    form_feedback = st.form('feedback')
    with form_feedback:
        feedback_title = st.text_input(label = "Title", max_chars = 50,value = "")
        feedback_text = st.text_input(label = "Feedback", max_chars = 300,value = "")
        feedback_name = st.text_input(label = "Name", max_chars = 50, placeholder = 'Optional',value = "")
        feedback_email = st.text_input(label = "Email", max_chars = 100, placeholder = 'Optional',value = "")

        # st.session_state['feedback'] = [feedback_name,feedback_email,feedback_title,feedback_text]
        #print(feedback_title,feedback_text,feedback_name,feedback_email) 
        feedback_form_submit = st.form_submit_button("Submit")
        
        if feedback_form_submit:
            todays_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            feedback = [feedback_name,feedback_email,feedback_title,feedback_text] + [todays_date]
            feedback_sheet.insert_row(feedback, 2)
            st.success("Feedback Submitted. Thank you!" ,icon = "✅")

st.write("---")
markdown_text = '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://www.linkedin.com/in/fernandeslloyd/"> Lloyd Fernandes</a> | <a href="https://www.linkedin.com/in/praveen-kumar-murugaiah-843415107/"> Praveen Kumar Murugaiah</a> | <a href="https://www.linkedin.com/in/raunak-sengupta-b62886107/"> Raunak Sengupta</a></h6>'
st.markdown(markdown_text, unsafe_allow_html=True)

         
        
        
    
    
        
        

    

    
  