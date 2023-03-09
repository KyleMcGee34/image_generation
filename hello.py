import streamlit as st
import streamlit_ext as ste
import requests
from PIL import Image, PngImagePlugin
import io
import base64
import datetime
import json
from zipfile import ZipFile
import os
import shutil


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
    seed = st.number_input('Enter Seed', value=-1, step=1)
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
    image_lst_multiple = []
    try:
        shutil.rmtree('images')
    except:
        pass
    os.makedirs('images')
    '''## Create multiple images'''
    left_column2, right_column2 = st.columns(2)
    button_clicked_multiple = False
    # Lets user input a positive prompt
    with left_column2:
        prompt1 = st.text_area('Enter Positive Prompt ', value=prompt)
    # Lets user input a negative prompt
    with right_column2:
        negative_prompt1 = st.text_area('Enter Negative Prompt ', value=negative_prompt)
    number_of_photos = st.number_input('How Many Photos Would You Like to Generate?', value=5, min_value=2,max_value=50)
    
    if st.button('Generate Images'):
        if password == st.secrets["password"]:
            progress_text = "Operation in progress. Please wait."
            my_bar = st.progress(0, text=progress_text)
            button_clicked_multiple = True
            x = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload, headers=headers)
            
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
            
            for num in range(number_of_photos):
                
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
                    image_lst_multiple.append(image)
                    image_lst_multiple[-1] = f'{num}_{now}_image.png'
                    image.save(f'images/{num}_{now}_image.png','PNG')
                with open(f'images/{num}_{now}_text.txt', 'w') as f:
                    dict_ = json.loads(r['info'])
                    for key, value in dict_.items():
                        f.write(f'{key}: {value}\n')

                seed = seed + 1
                my_bar.progress((num+1)/number_of_photos, text=progress_text)
        else:
            '''Password is incorrect'''
            
    col1, col2, col3 = st.columns(3)
    if button_clicked_multiple:
        with col1:
            with ZipFile(f'images.zip', 'w') as zipObject:
                for im in os.listdir('images/'):
                    if im.endswith('.png'):
                        zipObject.write(f'images/{im}')
            with open(f'images.zip', 'rb') as zipfile:
                ste.download_button('Download Image Zip File', zipfile, file_name=f'images.zip')
        with col2:
            with ZipFile(f'text.zip', 'w') as zipObjectText:
                for textF in os.listdir('images/'):
                    if textF.endswith('.txt'):
                        zipObjectText.write(f'images/{textF}')            
            with open(f'text.zip', 'rb') as zipFileText:
                ste.download_button('Download Text Zip File', zipFileText, file_name=f'text.zip')
        with col3:
            with ZipFile('images&text.zip', 'w') as zipObjectBoth:
                for both in os.listdir('images/'):
                    zipObjectBoth.write(f'images/{both}')
            with open(f'images&text.zip', 'rb') as zipFileBoth:
                ste.download_button('Download Image & Text Zip File', zipFileBoth, file_name=f'both.zip')        
        for img in os.listdir('images/'):
            if img.endswith('.png'):
                st.image(f'images/{img}')
        # st.image(image) # show the image