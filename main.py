import streamlit as st
import slack_sdk
import pandas as pd
import streamlit_extras.streaming_write as stsw
import streamlit_extras.colored_header as sech
import streamlit_extras.switch_page_button as stex
import streamlit_authenticator as stauth
from supabase import create_client
import cloudflare_CRUD as cf
import time
from pytz import timezone
import fitz      
import pandas as pd
import unicodedata
import os,io,fnmatch
import ast
import random
import streamlit_extras.mandatory_date_range as stcal
import datetime
import PIL.Image    
from streamlit_drawable_canvas import st_canvas
import json
import streamlit_lottie

## 온라인 게시용 수파 접속
@st.cache_resource
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)
supabase = init_connection()

firsttime = datetime.datetime.now().timestamp()
def streamdata(contents,duration: float = 0.1):
    for word in contents.split():
        yield word + " "
        time.sleep(duration)

@st.cache_data(ttl=60*60)
def data_load():
    response1= supabase.table('online_math_master').select('*').execute()
    df = pd.DataFrame(response1.data)
    name = df.name.to_list()
    user_id = df.username.to_list()
    user_pass = df.password.to_list()
    return name, user_id,user_pass
try:
    name, user_id,user_pass = data_load()
except:
    name,user_id,user_pass = [],[],[]

authenticator = stauth.Authenticate(name,user_id,user_pass,
                                    'Test1','abcdef',cookie_expiry_days=30)
with st.sidebar:
    name, authentication_status, username = authenticator.login('로그인','main')

    if authentication_status == False:
        st.error('아이디/비밀번호가 일치하지 않습니다.')
        
    if authentication_status == None:
        st.warning('아이디와 비밀번호를 입력하세요')
with st.sidebar:
    if authentication_status:
        st.session_state.auths = authenticator
        @st.cache_data(ttl=60*60)
        def load_inform():
            res = supabase.table('online_math_master').select('*').eq('username',st.session_state.username).execute()
            user_data = res.data[0]
            return user_data
        user_data = load_inform()
        expired_date = user_data['expired_date']
        st.subheader(f":green[{st.session_state.username}] 님, 안녕하세요")
            
        if 'logsoutview' not in st.session_state:
            st.session_state.logsoutview = False
        if st.session_state.logsoutview == False:
            logs = st.button('로그아웃')
            
            if logs:
                st.session_state.logsoutview = True
                st.cache_data.clear()
            
        if st.session_state.logsoutview == True:
            st.info('로그아웃합니다.')
            
            cols2 = st.columns(2)
            with cols2[0]:
                authenticator.logout('확인')
                
            with cols2[1]:
                cancelview = st.button('취소')
            if cancelview:
                st.session_state.logsoutview = False
                st.rerun()
appaddress = 'localhost:8501'
if 'authentication_status' not in st.session_state:
    st.header(f":red[로그인 후 이용할 수 있습니다.]")
    
else:
    if st.session_state.authentication_status==True:
        st.session_state.username
        SLACK_BOT_TOKEN = st.secrets['slack_token']
        SLACK_APP_TOKEN = st.secrets['slack_app_token']
        SLACK_SIGNING_SECRET = st.secrets['slack_signing_secret']
        # 채널 이름을 설정합니다.
        CHANNEL_NAME = "C06791EG3B4"
        # CHANNEL_NAME = "#math-project"
        
        @st.cache_resource
        def client_load():
            s_client = slack_sdk.WebClient(token=SLACK_BOT_TOKEN)
            return s_client
        
        s_client = client_load()
        
        
        
        if 'ttl001' not in st.session_state:
            st.session_state.ttl001 = 0
        if 'ttl002' not in st.session_state:
            st.session_state.ttl002 = 0
        if 'loaddf' not in st.session_state:
            st.session_state.loaddf = pd.DataFrame()
        
        @st.cache_data(ttl=st.session_state.ttl001)
        def load_history(channelid,limit:int=30):
            his = s_client.conversations_history(channel=channelid,limit=limit)
            his = his['messages']
            st.session_state.ttl001 = 600
            return his
        
        @st.cache_data(ttl=st.session_state.ttl002)
        def load_replies(CHANNEL_NAME,ts):
            his = s_client.conversations_replies(channel=CHANNEL_NAME,ts=ts)
            his = his['messages']
            st.session_state.ttl002 = 600
            return his
        
        
        
        # receive = st.button('RECEIVE')
        # if receive:
        #     text_receive = s_client.conversations_replies(channel=CHANNEL_NAME,ts='1700938880.902089')
        #     for i in range(len(text_receive['messages'])):
        #         text_receive['messages'][i]['text']
        #     # text_receive['messages']
        
        
        
        # s_client.chat_postMessage(channel=CHANNEL_NAME,text='Hellos')
        # his = s_client.conversations_history(channel='C06791EG3B4')
        # # his = s_client.conversations_history(channel=CHANNEL_NAME)
        # his['messages'][12]['blocks'][0]['elements']
        # with st.form('query',clear_on_submit=True):
        #     query = st.text_area('질문하기',placeholder='질문내용을 입력하세요.')
            
        #     send = st.form_submit_button('SEND')
        
        
        
        
        
        sech.colored_header(':blue[질문내역]', description='매일 :rainbow[OnePage]로 관리하는 실력향상 프로그램',color_name='blue-60')
        cols = st.columns(4)    
        with cols[3]:
            refresh = st.button('#### 새로고침',use_container_width=True)
            if refresh:
                st.session_state.ttl001 = 0
                st.session_state.ttl002 = 0
                st.rerun()
        with cols[2]:
            nums = st.number_input('자료개수', min_value=10,max_value=100,step=10,value=10)
        his = load_history(CHANNEL_NAME,nums)
        
        df = pd.DataFrame(his)
        df['선택'] = False
        
        df['작성일시'] = pd.to_datetime(df['ts'].astype(float)+9*3600,unit='s')
        # df['작성일시'] = df['작성일시'].dt.tz_localize('Asia/Seoul')
        st.session_state.loaddf = df
        # st.session_state.loaddf = st.session_state.loaddf.rename(columns={'text':'내용'})
        # st.session_state.loaddf = df.loc[:,['선택','작성일시','text','reply_count','user','ts','thread_ts']]
        # st.session_state.loaddf = st.session_state.loaddf.rename(columns={'text':'내용','reply_count':'댓글'})
        st.session_state.loaddf = st.session_state.loaddf.fillna(0)
        
        df2 = st.data_editor(st.session_state.loaddf,hide_index=True,use_container_width=True,disabled=['작성일시','내용','user','ts','댓글','thread_ts'])
        
        choidx = df2[df2['선택']==True].index
        if len(choidx)==0:
            pass
        elif len(choidx)==1:
            for idx in choidx:
                if df2.loc[idx,'댓글']!=0:
                    rep = load_replies(CHANNEL_NAME,df2.loc[idx,'ts'])
                    user=[]
                    for i in range(len(rep)):
                        user.append(rep[i]['user'])
                    with st.expander('대화목록',expanded=True):
                        for i,j in enumerate(user):
                            if i==0:
                                student = j
                            else:
                                pass
                            if student==j:
                                with st.chat_message(name='user',avatar='👨🏻‍🎓'):
                                    st.write(rep[i]['text'])
                            else:
                                with st.chat_message(name='assistant',avatar='🧑🏻‍🏫'):    
                                    st.write(rep[i]['text'])
                                
                                    try:
                                        
                                        for j in range(len(rep[i]['files'])):
                                        # for j in rep[i]['files']:
                                            # rep[i]['files'][j]
                                            rep[i]['files'][j]['url_private']
                                            rep[i]['files'][j]['url_private_download']
                                        st.caption('위 URL 주소를 참고하세요.')    
                                    except:
                                        pass
                else:
                    st.info('댓글이 없습니다.')
        else:
            st.info('질문은 한개씩 선택하세요.')
        
        query = st.chat_input('질문하기')
        
        if query:
            choidx = df2[df2['선택']==True].index
            if len(choidx)==0:
                res = s_client.chat_postMessage(channel=CHANNEL_NAME,text=query)
                st.session_state.ttl001 = 0
                st.rerun()
            elif len(choidx)==1:
                for idx in choidx:
                    if df2.loc[idx,'thread_ts']!=0:
                        s_client.chat_postMessage(channel=CHANNEL_NAME,text=query,thread_ts=df2.loc[idx,'thread_ts'])
                    else:
                        s_client.chat_postMessage(channel=CHANNEL_NAME,text=query,thread_ts=df2.loc[idx,'ts'])
                st.session_state.ttl001 = 0
                st.session_state.ttl002 = 0
                st.rerun()
            else:
                pass



def reruns():
    st.session_state.ttl001=0
    st.session_state.ttl002=0
    st.rerun()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
    

app = App(token=st.secrets['slack_token'])


@app.event("app_mention")  # 앱을 언급했을 때
def who_am_i(event, client, message, say):
    print('event:', event)
    print('client:', client)
    print('message:', message)
    
    say(f'hello! <@{event["user"]}>')
    reruns()
    # say(
    #         blocks=[
    #             {
    #                 "type": "section",
    #                 "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
    #                 "accessory": {
    #                     "type": "button",
    #                     "text": {"type": "plain_text", "text": "Click Me"},
    #                     "action_id": "button_click"
    #                 }
    #             }
    #         ],
    #         text=f"Hey there <@{message['user']}>!"
    #     )

@app.message("byebye")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )
    reruns()


def get_day_of_week():
    weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
 
    weekday = weekday_list[datetime.datetime.today().weekday()]
    date = datetime.datetime.today().strftime("%Y년 %m월 %d일")
    result = '{}({})'.format(date, weekday)
    return result
 
def get_time():
    return datetime.datetime.today().strftime("%H시 %M분 %S초")
 
 
def get_answer(text):
    trim_text = text.replace(" ", "")
 
    answer_dict = {
        '안녕': '안녕하세요. CheckMate입니다.',
        '요일': ':calendar: 오늘은 {}입니다'.format(get_day_of_week()),
        '시간': ':clock9: 현재 시간은 {}입니다.'.format(get_time()),
    }
 
    if trim_text == '' or None:
        return "알 수 없는 질의입니다. 답변을 드릴 수 없습니다."
    elif trim_text in answer_dict.keys():
        return answer_dict[trim_text]
    else:
        for key in answer_dict.keys():
            if key.find(trim_text) != -1:
                return "연관 단어 [" + key + "]에 대한 답변입니다.\n" + answer_dict[key]
 
        for key in answer_dict.keys():
            if answer_dict[key].find(text[1:]) != -1:
                return "질문과 가장 유사한 질문 [" + key + "]에 대한 답변이에요.\n"+ answer_dict[key]
 
    return text + "은(는) 없는 질문입니다."


import re

@app.message(re.compile("(hi|hello|hey|반가워)"))
def say_hello_regex(say, context):
    # regular expression matches are inside of context.matches
    greeting = context['matches'][0]
    say(f"{greeting}, how are you?")
    

@app.message(re.compile("(안녕|요일|시간)"))
def say_hello_regex(say, context):
    # regular expression matches are inside of context.matches
    greeting = context['matches'][0]
    # say(f"{greeting}, how are you?")
    say(f"{get_answer(greeting)}")
    

@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")
    


# Start your app
if __name__ == '__main__':
    SocketModeHandler(app, st.secrets['slack_app_token']).start()
