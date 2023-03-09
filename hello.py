import streamlit as st
import streamlit_ext as ste
import requests
from PIL import Image, PngImagePlugin
import io
import base64
import datetime
import json


'''# Fake Image Generation GUI'''
url = "https://sd-darpa-02.chris-mckinley.website"

password = st.text_input("ENTER PASSWORD", type='password')
headers = {'CF-Access-Client-Id': st.secrets["client_id"],
           'CF-Access-Client-Secret': st.secrets["client_secret"]}

with st.sidebar:
    model = st.selectbox('Select a Model',
                         ['SD15NewVAEpruned.ckpt [27a4ac756c]', 'SDv2.1.ckpt'])
    sampler_index = st.selectbox('Select a Sampler',
                                 ['Euler a', 'Euler', 'LMS', 'Heun', 'DPM2', 'DPM2 a', 'DPM++ 2S a', 'DPM++ 2M', 'DPM++ SDE', 'DPM fast', 'DPM adaptive', 'LMS Karras', 'DPM2 Karras', 'DPM2 a Karras', 'DPM++ 2S a Karras', 'DPM++ 2M Karras', 'DPM++ SDE Karras', 'DDIM', 'PLMS'])
    cfg_scale = st.slider('Choose CFG scale',
                          0.0,10.0,7.0,0.1)
    steps = st.slider("Number of Steps",
                      1,50,20,1)
    seed = st.text_input('Enter Seed', -1)
    height = st.number_input('Enter Height of Picture', value=512, min_value=64,max_value=2048)
    width = st.number_input('Enter Width of Picture', value=512, min_value=64, max_value=2048)
    
tab1, tab2 = st.tabs(["Create One Image", "Create Multiple Images"])

with tab1:
    '''## Create one image'''
    left_column1, right_column1 = st.columns(2)

    # Lets user input a positive prompt
    with left_column1:
        prompt = st.text_area('Enter Positive Prompt')
    # Lets user input a negative prompt
    with right_column1:
        negative_prompt = st.text_area('Enter Negative Prompt')
    # Used to set the model for image generation
    option_payload = {
        "sd_model_checkpoint": model
    }

    image_lst = [] # stores the images
    # Controls the download image and text buttons below
    button_clicked = False 

    if st.button('Generate Image'):
        if password == st.secrets["password"]:
            button_clicked = True
            x = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload, headers=headers)
            
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
            
            payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "height": height,
            "width": width,
            "sampler_index": sampler_index,
            "seed": seed
        }

            response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload, headers=headers)

            r = response.json()
            for i in r['images']:
                image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
                image_lst.append(image)
                image_lst[-1] = f'image_{now}.png'
                image.save(f'image_{now}.png','PNG')
            with open(f'text_{now}.txt', 'w') as f:
                dict_ = json.loads(r['info'])
                for key, value in dict_.items():
                    f.write(f'{key}: {value}\n')
        else:
            '''Password is incorrect'''
            
    col1, col2 = st.columns(2)
    if button_clicked:
        with col1:
            with open(f'image_{now}.png', 'rb') as file:
                ste.download_button('Download Image', file, file_name=f'image_{now}.png')
        with col2:
            with open(f'text_{now}.txt', 'rb') as textfile:
                ste.download_button('Download Text File', textfile, file_name=f'text_{now}.txt')
        st.image(image) # show the image
with tab2:
    '''## Create multiple images'''