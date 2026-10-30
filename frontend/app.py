import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title='AirAware',layout='centered')
st.title('AirAware')
st.caption('Telugu–English Code-Mixed Agentic AI Chatbot | Small Delhi air pollution pilot')
endpoint=st.sidebar.radio('Workflow', ['n8n automation','Direct API (test mode)'])
st.sidebar.markdown('**LLM:** Gemini 2.5 Flash (configured in `.env`)')
st.sidebar.markdown('**Backend:** FastAPI + SQLite')
st.sidebar.markdown('**n8n:** Webhook → Gemini plan → Analytics → Response')
st.sidebar.markdown('Example: `Delhi lo PM2.5 average entha?`')
st.sidebar.markdown('Example: `Show PM10 trend graph`')
st.sidebar.markdown('Example: `Compare Delhi monitoring stations for NO2`')
if 'messages' not in st.session_state: st.session_state.messages=[]
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.write(msg['text'])
        if msg.get('rows'):
            frame=pd.DataFrame(msg['rows'])
            st.dataframe(frame,use_container_width=True)
            if 'date' in frame and 'value' in frame: st.line_chart(frame.set_index('date')['value'])
            elif 'station' in frame and 'value' in frame: st.bar_chart(frame.set_index('station')['value'])
question=st.chat_input('Ask about Delhi pollution in Telugu, English, or both...')
if question:
    st.session_state.messages.append({'role':'user','text':question})
    with st.chat_message('user'): st.write(question)
    with st.chat_message('assistant'):
        try:
            if endpoint=='n8n automation':
                url=os.getenv('N8N_WEBHOOK_URL','http://localhost:5678/webhook/airaware-query')
            else:
                url=os.getenv('BACKEND_URL','http://localhost:8000').rstrip('/')+'/process'
            response=requests.post(url,json={'question':question},timeout=90)
            response.raise_for_status()
            data=response.json()
            if isinstance(data,list): data=data[0]
            st.write(data.get('answer','No response returned'))
            if data.get('rows'):
                frame=pd.DataFrame(data['rows']); st.dataframe(frame,use_container_width=True)
                if 'date' in frame and 'value' in frame: st.line_chart(frame.set_index('date')['value'])
                elif 'station' in frame and 'value' in frame: st.bar_chart(frame.set_index('station')['value'])
            st.caption('Query engine: '+str(data.get('model_used','not reported')))
            st.session_state.messages.append({'role':'assistant','text':data.get('answer',''),'rows':data.get('rows',[])})
        except Exception as exc:
            st.error(f'Request failed: {exc}. Make sure backend is running and n8n workflow is active, or select Direct API (test mode).')
