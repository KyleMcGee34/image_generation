import streamlit as st
import requests
from PIL import Image, PngImagePlugin
import io
import base64


'''# This is a title'''
url = "https://sd-darpa-02.chris-mckinley.website"

client_id = st.text_input('Client ID','014d7d201690e107491b1286e5910dd2.access')
client_secret = st.text_input('Client Secret','518671b12e6f8c7f624ce5defd88540a977e300b723892cdfaebca5e6c59b58f')

headers = {'CF-Access-Client-Id': client_id,
           'CF-Access-Client-Secret': client_secret}

left_column, right_column = st.columns(2)
with left_column:
    model = st.selectbox('Select a Model',
                         ['SD15NewVAEpruned.ckpt [27a4ac756c]', 'SDv2.1.ckpt'])
    
with right_column:
    sampler_index = st.selectbox('Select a Sampler',
                                 ['Euler a', 'Euler', 'LMS', 'Heun', 'DPM2', 'DPM2 a', 'DPM++ 2S a', 'DPM++ 2M', 'DPM++ SDE', 'DPM fast', 'DPM adaptive', 'LMS Karras', 'DPM2 Karras', 'DPM2 a Karras', 'DPM++ 2S a Karras', 'DPM++ 2M Karras', 'DPM++ SDE Karras', 'DDIM', 'PLMS'])
    
left_column1, right_column1 = st.columns(2)

with left_column1:
    prompt = st.text_input('Enter Positive Prompt')

with right_column1:
    negative_prompt = st.text_input('Enter Negative Prompt')

left_column2, right_column2 = st.columns(2)
with left_column2:
    cfg_scale = st.slider('Choose CFG scale',
                          0.0,10.0,7.0,0.1)

# Or even better, call Streamlit functions inside a "with" block:
with right_column2:
    steps = st.slider("Number of Steps",
                      1,50,20,1)

option_payload = {
    "sd_model_checkpoint": model
}
 
 
# x = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload, headers=headers)
# print(x)
if st.button('Generate Images'):
    x = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload, headers=headers, stream=True, timeout=5)
    print(x)
    
    payload = {
    "prompt": prompt
    "negative_prompt": negative_prompt,
    "steps": 20,
    "cfg_scale": 7,
    "height": 512,
    "width": 512,
    "sampler_index": 'Euler a',
    "seed": 2219603864
}

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload, headers=headers)

    r = response.json()
    image_lst = [] # stores the images
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        image_lst.append(image)
            
    st.image(image)
else:
    pass