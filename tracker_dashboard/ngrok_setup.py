import subprocess
import threading
import os
from pyngrok import ngrok, conf

def run_ngrok():
    # ngrok authtoken
    ngrok.set_auth_token("2gcTed5OlN8yYDICnjYmEGp5IdP_7XrNbqhYHgPoxvZ7G8qxU")

    # Use the static domain
    public_url = ngrok.connect(8501, bind_tls=True, hostname="crucial-jaybird-immense.ngrok-free.app")
    print(f'Public URL: {public_url}')

def run_streamlit():
    os.system('streamlit run app.py')

ngrok_thread = threading.Thread(target=run_ngrok)
ngrok_thread.start()

streamlit_thread = threading.Thread(target=run_streamlit)
streamlit_thread.start()

ngrok_thread.join()
streamlit_thread.join()