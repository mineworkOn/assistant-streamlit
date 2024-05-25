import streamlit as st
from openai import OpenAI
import time

api_key = st.secrets["openai_key"]
assistant_id = st.secrets["assistant_id"]

@st.cache_resource
def load_openai_client_and_assistant():
    client = OpenAI(api_key=api_key)
    my_assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create()

    return client, my_assistant, thread

client, my_assistant, assistant_thread = load_openai_client_and_assistant()

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.run.retrieve(
            thread_id = thread.id,
            run_id = run.id
        )
        time.sleep(0.5)

    return run

def get_assistant_response(user_input = ""):
    message = client.beta.threads.messages.create(
        thread_id = assistant_thread.id,
        role = "user",
        content = user_input
    )
    run = client.beta.threads.runs.create(
        thread_id = assistant_thread.id,
        assistant_id = assistant_id
    )
    run = wait_on_run(run, assistant_thread)

    messages = client.beta.threads.messages.list(
        thread_id = assistant_thread.id, order = "asc", after = message.id
    )

    return messages.data[0].content[0].text.value

if 'user_input' not in st.session_state:
    st.session_state.user_input = ''

def submit():
    st.session_state.user_input = st.session_state.query
    st.session_state.query = ''

st.title("Obamacare Health Insurance Assistant")
st.text_input("Ask me: ", key = 'query', on_change = submit)
user_input = st.session_state.user_input
st.write("Your Question: ", user_input)

if user_input:
    result = get_assistant_response(user_input)
    st.header('Assistant :blue[cool] :Obamacare:', divider = 'rainbow')
    st.text(result)