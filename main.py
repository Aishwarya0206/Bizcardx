import streamlit as st
import easyocr # (Optical Character Recognition)
import numpy as np
import PIL
from PIL import Image, ImageDraw
import cv2
import os
import re
import io
from dataHandler import dataHandler


# Upload the images and extract the informations
def get_img():
    upload_imgs = st.file_uploader(':blue[Select business cards to extract the information (Image file)]', type =['png','jpg', "jpeg"], accept_multiple_files=True)
    st.info(''':blue[File extension must be PNG, JPG, JPEG, Uploaded files are limited to 200MB, Language : English]''')
    #print(upload_imgs)
    confirmation = ""
    if(upload_imgs is not None):
        for upload_img in upload_imgs:
            try:
                with st.spinner("Extracting the information & uploading to database..."):
                    bytes_data = upload_img.read()
                    reader = easyocr.Reader(['en'], gpu=False)
                    if(isinstance(upload_img, str)):
                        img = Image.open(upload_img)
                    elif isinstance(upload_img, Image.Image):
                        img = upload_img
                    else:
                        img = Image.open(upload_img)

                    img_arr = np.array(img)
                    img_read = reader.readtext(img_arr)
                    
                    result = []
                    for read in img_read:
                        result.append(read[1].strip(''))

                
                    data = {"image": "",
                        "Details":{
                        "Company_name": "",
                        "Card_holder": "",
                        "Designation": "",
                        "Mobile_number": [],
                        "Email": [],
                        "Website": [],
                        "Area": [],
                        "City": [],
                        "State": [],
                        "Pin_code": [],
                        }
                        }
                    data["image"] = upload_img.name
                    city = ""  
                    for index, i in enumerate(result):
                        print(index, i)
                        if "WWW" in i:
                            if("WWW" == i):
                                data["Details"]["Website"] =  None
                            else:
                                website = i.split(' ')
                                data["Details"]["Website"].append(website[0].lower() + "." + website[1].lower())
                        elif "www " in i.lower() or "www." in i.lower():
                            print(i.lower())
                            data["Details"]["Website"].append(i.lower())

                        elif "@" in i:
                            data["Details"]["Email"].append(i.lower())

                        elif "-" in i:
                            data["Details"]["Mobile_number"].append(i)
                                
                        elif index == len(result) - 1:
                            data["Details"]["Company_name"] = i.capitalize()

                        #elif index == len(result) - 1:
                        #    data["Details"]["Company_name"] = data["Details"]["Company_name"] + i.capitalize()

                        elif index == 0:
                            data["Details"]["Card_holder"] = i.capitalize()

                        elif index == 1:
                            data["Details"]["Designation"] = i.capitalize()

                        if re.findall("^[0-9].+, [a-zA-Z]+", i):
                            data["Details"]["Area"].append(i.split(",")[0].strip())
                        elif re.findall("[0-9] [a-zA-Z]+", i):
                            data["Details"]["Area"].append(i.strip())

                        match1 = re.findall(".+St , ([a-zA-Z]+).+", i)
                        match2 = re.findall(".+St,, ([a-zA-Z]+).+", i)
                        match3 = re.findall("^[E].*", i)
                        if match1 and match1[0] != '':
                            city = match1[0].strip() # Assign the matched city value
                        elif match2 and match2[0] != '':
                            city = match2[0].strip()  # Assign the matched city value
                        elif match3 and match3[0] != '':
                            city = match3[0].strip()  # Assign the matched city value
                            
                        state_match = re.findall("[a-zA-Z]{9} +[0-9]", i)
                        if state_match:
                            data["Details"]["State"].append(i[:9])
                        elif re.findall("^[0-9].+, ([a-zA-Z]+);", i):
                            data["Details"]["State"].append(i.split()[-1].replace(';', ''))
                        if len(data["Details"]["State"]) == 2:
                            data["Details"]["State"].pop(0)

                        if len(i) >= 6 and i.isdigit():
                            data["Details"]["Pin_code"].append(i)
                        elif re.findall("[a-zA-Z]{9} +[0-9]", i):
                            data["Details"]["Pin_code"].append(i[10:])
                    data["Details"]["City"].append(city.replace(',', ''))
                    confirmation = sql_conn.insert_bizcardx(connect['cursor'], connect['conn'], data)
                
            except Exception as e:
                st.info("Error in get_img "+str(e))
        if(confirmation != ''):
            st.info("Extracted and uploaded to the database")
    else:
        st.warning(''':red[Upload an image]''')

    
        
#View in table
def table():
    st.header("Bizcardx Table View")
    bizCardxDataFrame = sql_conn.select_from_bizcardx(connect['cursor'], connect['conn'])
    st.dataframe(bizCardxDataFrame)


if __name__ == '__main__':
    # DB connection
    sql = {"host": "localhost", "user": "root", "password": "Password123#@!","database":"BizCardx"}
    sql_conn = dataHandler(sql)
    connect = sql_conn.connect_db()
    create_table_ddl = sql_conn.execute_ddl(connect['cursor'], connect['conn'])

    page_names_to_funcs = {
            "Get Bizcardx": get_img,
            "Bizcardx View": table
        }
    app_name = st.sidebar.selectbox(":blue[Choose a Bizcardx view]", page_names_to_funcs.keys())
    page_names_to_funcs[app_name]()

