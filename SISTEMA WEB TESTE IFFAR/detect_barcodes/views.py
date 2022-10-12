import os
from symbol import shift_expr
import time
from datetime import datetime
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import simpleaudio as sa

name = 0

class CameraStreamingWidget:
    def __init__(self):
        self.camera = cv2.VideoCapture(int(os.environ.get('CAMERA')))
        self.media_path = os.path.join(os.getcwd(), "media", "images")

    def get_frames(self):
        while True:
            success, frame = self.camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                color_image = np.asanyarray(frame)

                if decode(color_image):

                    for barcode in decode(color_image):
                        barcode_data = (barcode.data).decode('utf-8')
                        if barcode_data:
                            if name != 0:
                                file = open(os.path.join(os.getcwd(), 'dados', f'{name}.txt'),"r")
                                content = file.read()
                                file.close()

                                if barcode_data in content:
                                    pass
                                else:
                                    wave_obj = sa.WaveObject.from_wave_file(os.path.join(os.getcwd(), 'utils', 'beep_sound.wav'))
                                    wave_obj.play()

                                    dia = str(datetime.now().strftime("%d-%m-%Y"))
                                    hora = str(datetime.now().strftime("%H:%M:%S"))

                                    fil = open(os.path.join(os.getcwd(), 'dados', f'{name}.txt'),"a")
                                    fil.write(f'{barcode_data} | {hora} | {dia}')
                                    fil.write('\n')
                                    fil.close()



                            pts = np.array([barcode.polygon], np.int32)
                            pts = pts.reshape((-1,1,2))
                            # draw polylines on the barcode
                            cv2.polylines(
                                img=color_image,
                                pts=[pts],
                                isClosed=True,
                                color=(0,255,0),
                                thickness=2
                            )
                            pts2 = barcode.rect

                            barcode_frame = cv2.putText(
                                img=color_image,
                                text=barcode_data,
                                org=(pts2[0], pts2[1]),
                                fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                                fontScale=0,
                                color=(0,0,255),
                                thickness=2
                            )
                            _, buffer_ = cv2.imencode('.jpg', barcode_frame)

                            barcode_frame = buffer_.tobytes()

                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + barcode_frame + b'\r\n\r\n')
                else:
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Camera feed
def camera_feed(request):
    stream = CameraStreamingWidget()
    frames = stream.get_frames()

    return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')


def detect(request):
    stream = CameraStreamingWidget()
    success, frame = stream.camera.read()
    if success:
        status = True
    else:
        status = False
    return render(request, 'detect_barcodes/detect.html', context={'cam_status': status})

def dados(request):
    if request.method == 'POST':
        global name
        name = request.POST['name'] 

        IsExist = os.path.exists(os.path.join(os.getcwd(), 'dados', f'{name}.txt'))

        if not IsExist:
            file = open(os.path.join(os.getcwd(), 'dados', f'{name}.txt'), 'x')

        return HttpResponse(name)

def dados_cod(request):
    if request.method == 'POST':
        cod = request.POST['cod']

        if name != 0:
            file = open(os.path.join(os.getcwd(), 'dados', f'{name}.txt'),"r")
            content = file.read()
            file.close()

            if cod in content:
                pass
            else:
                dia = str(datetime.now().strftime("%d-%m-%Y"))
                hora = str(datetime.now().strftime("%H:%M:%S"))

                fil = open(os.path.join(os.getcwd(), 'dados', f'{name}.txt'),"a")
                fil.write(f'{cod} | {hora} | {dia}')
                fil.write('\n')
                fil.close()


        return HttpResponse(cod)
