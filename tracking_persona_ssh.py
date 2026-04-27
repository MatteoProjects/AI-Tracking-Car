from picamera2 import Picamera2
import cv2
import time
import requests

# ----------------------------
# CONFIG
# ----------------------------
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
ESP32_URL = "http://esp32.local/cmd"

PROTOTXT = "../modello/MobileNetSSD_deploy.prototxt"
MODEL = "../modello/MobileNetSSD_deploy.caffemodel"

CONFIDENCE_THRESHOLD = 0.5

LEFT_THRESHOLD = 0.38
RIGHT_THRESHOLD = 0.62

FAR_AREA_RATIO = 0.07
NEAR_AREA_RATIO = 0.22

# Memoria: quanti frame senza detection prima di dire NESSUNA_PERSONA
MAX_MISSING_FRAMES = 10

# Intervallo minimo di stampa
PRINT_INTERVAL = 0.3

# Classe "person" in MobileNet SSD
CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant",
    "sheep", "sofa", "train", "tvmonitor"
]
PERSON_CLASS_ID = CLASSES.index("person")

def invia_a_esp32(messaggio):
    try:
        r = requests.get(ESP32_URL, params={"msg": messaggio}, timeout=1.0)
        print(f"HTTP {r.status_code}: {r.text}")
        return r.status_code == 200
    except requests.RequestException as e:
        print(f"Errore HTTP verso ESP32: {e}")
        return False

def classifica_posizione(cx, frame_width):
    x_norm = cx / frame_width
    if x_norm < LEFT_THRESHOLD:
        return "SINISTRA"
    elif x_norm > RIGHT_THRESHOLD:
        return "DESTRA"
    else:
        return "CENTRO"


def classifica_distanza(area_ratio):
    if area_ratio < FAR_AREA_RATIO:
        return "LONTANA"
    elif area_ratio > NEAR_AREA_RATIO:
        return "VICINA"
    else:
        return "MEDIA"


# ----------------------------
# LOAD MODEL
# ----------------------------
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)

# ----------------------------
# CAMERA
# ----------------------------
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (FRAME_WIDTH, FRAME_HEIGHT)}
)
picam2.configure(config)
picam2.start()
time.sleep(2)

print("Tracking avviato. Esci con CTRL+C.")

ultimo_stato_stampato = None
ultimo_tempo_stampa = 0

ultimo_stato_valido = "NESSUNA_PERSONA"
missing_frames = 0

try:
    ultimo_stato_inviato = None
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        h, w = frame_bgr.shape[:2]

        # Prepara input per rete
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame_bgr, (300, 300)),
            scalefactor=0.007843,
            size=(300, 300),
            mean=127.5
        )
        net.setInput(blob)
        detections = net.forward()

        best_conf = 0
        best_box = None

        # Cerca la persona migliore
        for i in range(detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])
            class_id = int(detections[0, 0, i, 1])

            if class_id == PERSON_CLASS_ID and confidence > CONFIDENCE_THRESHOLD:
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                x1, y1, x2, y2 = box.astype("int")

                # Correggi limiti
                x1 = max(0, min(x1, w - 1))
                y1 = max(0, min(y1, h - 1))
                x2 = max(0, min(x2, w - 1))
                y2 = max(0, min(y2, h - 1))

                bw = max(0, x2 - x1)
                bh = max(0, y2 - y1)

                # Scarta box troppo piccoli
                if bw < 40 or bh < 80:
                    continue

                if confidence > best_conf:
                    best_conf = confidence
                    best_box = (x1, y1, bw, bh)

        if best_box is not None:
            x, y, bw, bh = best_box
            cx = x + bw // 2

            area_box = bw * bh
            area_ratio = area_box / (w * h)

            posizione = classifica_posizione(cx, w)
            distanza = classifica_distanza(area_ratio)

            ultimo_stato_valido = f"{posizione}_{distanza}"
            missing_frames = 0

        else:
            missing_frames += 1

        # Mantieni l'ultimo stato valido per qualche frame
        if missing_frames <= MAX_MISSING_FRAMES:
            stato_corrente = ultimo_stato_valido
        else:
            stato_corrente = "NESSUNA_PERSONA"

        adesso = time.time()
        if (stato_corrente != ultimo_stato_stampato) or ((adesso - ultimo_tempo_stampa) > PRINT_INTERVAL):
            print(stato_corrente)
            ultimo_stato_stampato = stato_corrente
            ultimo_tempo_stampa = adesso

        # Invia solo quando cambia davvero stato
        if stato_corrente != ultimo_stato_inviato:
            ok = invia_a_esp32(stato_corrente)
            if ok:
                print(f"Inviato a ESP32: {stato_corrente}")
                ultimo_stato_inviato = stato_corrente
            else:
                print("Errore invio ESP32")

        time.sleep(0.03)

except KeyboardInterrupt:
    print("\nProgramma terminato.")

finally:
    picam2.stop()
