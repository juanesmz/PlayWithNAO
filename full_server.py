from naoqi import ALProxy
import socket
import argparse
import cv2
import pickle
from multiprocessing import Process

# Conectar con el robot NAO (reemplaza la IP y el puerto con los de tu robot)
ip = "127.0.0.1"
port = 9559

def recibir_mensajes(server_ip):
    message_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message_socket.bind(('0.0.0.0', 6667))

    leds = ALProxy("ALLeds", ip, port)
    posture = ALProxy("ALRobotPosture", ip, port)
    animation = ALProxy("ALAnimationPlayer", ip, port)
    motion = ALProxy("ALMotion", ip, port)
    tts = ALProxy("ALTextToSpeech", ip, port)

    tts.setParameter('speed', 70)
    tts.setVolume(0.7)
    tts.setLanguage('Spanish')
    
    animations = {
        'hi': 'animations/Stand/Gestures/Hey_1',
        'correct': 'animations/Stand/Gestures/Yes_2',
        'incorrect': 'animations/Stand/Gestures/No_9',
    }

    while True:
        data, addr = message_socket.recvfrom(1024)
        message = str(data.decode('utf-8')).split()

        print("Mensaje recibido de {}: {}".format(addr, message))

        if message[0] == "led":
            if message[1] == "on":
                leds.on(message[2])
            elif message[1] == "off":
                leds.off(message[2])
            elif message[1] == "fade":
                leds.fadeRGB(message[2], float(message[3]), float(message[4]), float(message[5]), float(message[6]))
        elif message[0] == "posture":
            if message[1] == "stand":
                posture.goToPosture("Stand", 0.5)
            elif message[1] == "sit":
                posture.goToPosture("Sit", 0.5)
        elif message[0] == "stiffness":
            if message[1] == "on":
                motion.setStiffnesses("Body", 1.0)
            elif message[1] == "off":
                motion.setStiffnesses("Body", 0.0)
        elif message[0] == "motion":
            if message[1] == 'positive':
                motion.changeAngles(message[2], 0.05, 0.03)
            elif message[1] == 'negative':
                motion.changeAngles(message[2], -0.05, 0.03)
            msg = motion.getAngles('HeadPitch', True)
            message_socket.sendto(str(msg[0]).encode('utf-8'), (server_ip, 6668))
        elif message[0] == 'setHead':
            motion.setAngles('HeadPitch', float(message[1]), 0.3)
        elif message[0] == "animation":
            if message[1] in animations:
                animation.run(animations[message[1]])
        elif message[0] == 'say':
            tts.say(message[1].replace(';', ' '))


def enviar_video(server_ip):
    # Preparar NAO para no interferir con el video
    try:
        awareness = ALProxy("ALBasicAwareness", ip, port)
        awareness.stopAwareness()
    except: pass

    try:
        life = ALProxy("ALAutonomousLife", ip, port)
        if life.getState() != "disabled":
            life.setState("disabled")
    except: pass

    try:
        tracker = ALProxy("ALTracker", ip, port)
        if tracker.isActive():
            tracker.stopTracker()
    except: pass

    try:
        video = ALProxy("ALVideoDevice", ip, port)
        for device in video.getSubscribers():
            try:
                video.unsubscribe(device)
            except: pass
    except: pass

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000)
    cap = cv2.VideoCapture(0)

    while True:
        try:
            ret, img = cap.read()
            ret, buffer = cv2.imencode(".jpg", img[0:360,:,:], [int(cv2.IMWRITE_JPEG_QUALITY), 30])
            x_as_bytes = pickle.dumps(buffer)
            s.sendto(x_as_bytes, (server_ip, 6666))
        except KeyboardInterrupt:
            break

    cap.release()
    s.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_ip', required=True, help='IP del servidor')
    args = parser.parse_args()

    p1 = Process(target=recibir_mensajes, args=(args.server_ip,))
    p2 = Process(target=enviar_video, args=(args.server_ip,))

    p1.start()
    p2.start()

    try:
        p1.join()
        p2.join()
    except KeyboardInterrupt:
        p1.terminate()
        p2.terminate()
