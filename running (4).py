from flask import Flask, Response
from flask_cors import CORS, cross_origin
from flask import request
import os
import json
import numpy as np
import base64
import time
import cv2
from PIL import Image
from io import BytesIO

version = "1.1.2"
current_path = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type:application/json'


@app.route("/run", methods=["POST", "GET"])
@cross_origin(origin='*')
def run():
    start_time = time.time()
    try:
        imgstring = request.form.get('base64')
        sbuf = BytesIO()
        sbuf.write(base64.b64decode(imgstring))
        pimg = Image.open(sbuf)
        img = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # lower mask (0-10)
        lower_red = np.array([0, 50, 50])
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

                if (c[0][0] > 230 and c[0][0] < 400 and c[0][1] < 430 and c[0][1] > 400 and len(contour) < 300 and len(contour) > 120):
                    ischeck = True
            if (ischeck == True):
                haveCard = True
        return Response(json.dumps({"error_code": 0, "version": version, "message": "Thành công", "data": {"predictions": {"have_cards": haveCard, "time": time.time()-start_time}}}), mimetype='application/json')

    except Exception as e:
        return json.dumps({"error_code": -1, "message": "ERROR: " + str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='888', debug=True)
