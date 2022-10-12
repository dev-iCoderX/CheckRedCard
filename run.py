import os
import numpy as np
import base64
import time
import cv2
from PIL import Image
from io import BytesIO
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from datetime import datetime

class Item(BaseModel):
    base64: str

app = FastAPI()
version = "1.1.3"
current_path = os.path.dirname(os.path.abspath(__file__))
size = 1200, 674
#pimg.thumbnail(size, Image.ANTIALIAS)
def GetTime():
    now = datetime.now()
    dtString = "./img/"+now.strftime("%d-%m-%Y_%H-%M-%S")+".jpg"
    return dtString

def run(base64String):
    start_time = time.time()
    try:
        imgstring = base64String
        sbuf = BytesIO()
        sbuf.write(base64.b64decode(imgstring))
        pimg = Image.open(sbuf)
        pimg.thumbnail(size, Image.ANTIALIAS)
        img = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # lower mask (0-10)
        lower_red = np.array([0,150,100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(img_hsv, lower_red, upper_red)

        image = img.copy()
        image[np.where(mask == 0)] = 0
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        contours, hierarchy = cv2.findContours(
            gray_image,  cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        haveCard = False
        for contour in contours:
            ischeck = False
            for c in contour:
                if(c[0][0]>230 and c[0][0]<400 and c[0][1]<430  and c[0][1]>400 and len(contour)<300 and len(contour)>110):
                    ischeck = True
                    break
            if (ischeck == True):
                haveCard = True
                with open(GetTime(), 'wb') as f:
                    f.write(base64.b64decode(base64String))
                break
        return {"error_code": 0, "version": version, "message": "Thành công", "data": {"predictions": {"have_cards": haveCard, "time": time.time()-start_time}}}

    except Exception as e:
        return {"error_code": -1, "message": "ERROR: " + str(e)}


@app.post("/CheckRedCard")
async def create_item(item: Item):
    return run(item.base64)


if __name__ == "__main__":
    uvicorn.run(app, port=8001)


# Email: enzonasi8@gmail.com

# Password: @Qazplm1