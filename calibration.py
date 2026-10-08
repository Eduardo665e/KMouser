import cv2
import json
import time
import tkinter as tk
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CAMERA_INDEX = 0

MODEL_HAND = "models/hand_landmarker.task"
MODEL_FACE = "models/face_landmarker.task"

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

HEAD_CAMERA_DISTANCE_CM = 78.0

WINDOW_NAME = "KMouser Calibration"

JSON_FILE = "calibration.json"


# ============================================================
# RESOLUÇÃO DO MONITOR
# ============================================================

root = tk.Tk()
root.withdraw()

SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()

root.destroy()


# ============================================================
# PONTOS DO MONITOR
#
# x/y são coordenadas reais do monitor.
#
# 0,0       = canto superior esquerdo
# 1,1       = canto inferior direito
#
# Usamos uma pequena margem para que o alvo fique visível.
# ============================================================

CALIBRATION_POINTS = [

    {
        "name": "TOP_LEFT",
        "x": 0.02,
        "y": 0.02
    },

    {
        "name": "TOP_RIGHT",
        "x": 0.98,
        "y": 0.02
    },

    {
        "name": "CENTER",
        "x": 0.50,
        "y": 0.50
    },

    {
        "name": "BOTTOM_LEFT",
        "x": 0.02,
        "y": 0.98
    },

    {
        "name": "BOTTOM_RIGHT",
        "x": 0.98,
        "y": 0.98
    }

]


# ============================================================
# MEDIA PIPE - HAND
# ============================================================

base_options_hand = python.BaseOptions(
    model_asset_path=MODEL_HAND
)

hand_options = vision.HandLandmarkerOptions(
    base_options=base_options_hand,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2
)

hand_detector = vision.HandLandmarker.create_from_options(
    hand_options
)


# ============================================================
# MEDIA PIPE - FACE
# ============================================================

base_options_face = python.BaseOptions(
    model_asset_path=MODEL_FACE
)

face_options = vision.FaceLandmarkerOptions(
    base_options=base_options_face,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1
)

face_detector = vision.FaceLandmarker.create_from_options(
    face_options
)


# ============================================================
# CONECTAR À CÂMERA
# ============================================================

def connect_camera():

    while True:

        print("Tentando conectar à webcam...")

        cap = cv2.VideoCapture(
            CAMERA_INDEX
        )

        if cap.isOpened():

            cap.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                CAMERA_WIDTH
            )

            cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                CAMERA_HEIGHT
            )

            success, frame = cap.read()

            if success and frame is not None:

                print("Webcam detectada.")

                return cap

            cap.release()

        print("Webcam não disponível.")
        print("Verifique a chave física da câmera.")
        print("Tentando novamente em 2 segundos...")
        print()

        time.sleep(2)


# ============================================================
# DADOS DA CALIBRAÇÃO
# ============================================================

calibration_data = []


# ============================================================
# SALVAR JSON
# ============================================================

def save_calibration():

    data = {

        "version": 1,

        "screen": {

            "width": SCREEN_WIDTH,
            "height": SCREEN_HEIGHT

        },

        "head_camera_distance_cm":
            HEAD_CAMERA_DISTANCE_CM,

        "camera": {

            "index": CAMERA_INDEX,
            "width": CAMERA_WIDTH,
            "height": CAMERA_HEIGHT

        },

        "points": calibration_data

    }


    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


# ============================================================
# TEXTO
# ============================================================

def draw_text(
    frame,
    text,
    position,
    scale=1.0,
    thickness=2
):

    cv2.putText(

        frame,
        text,
        position,

        cv2.FONT_HERSHEY_SIMPLEX,

        scale,

        (255, 255, 255),

        thickness,

        cv2.LINE_AA

    )


# ============================================================
# ALVO
# ============================================================

def draw_target(
    frame,
    x,
    y
):

    # círculo externo
    cv2.circle(
        frame,
        (x, y),
        8,
        (255, 255, 255),
        2
    )

    # ponto central
    cv2.circle(
        frame,
        (x, y),
        2,
        (255, 255, 255),
        -1
    )


# ============================================================
# INÍCIO
# ============================================================

print()
print("========================================")
print("       KMouser Calibration")
print("========================================")
print()

print(
    f"Monitor: "
    f"{SCREEN_WIDTH} x {SCREEN_HEIGHT}"
)

print(
    f"Distância cabeça/câmera: "
    f"{HEAD_CAMERA_DISTANCE_CM} cm"
)

print()

cap = connect_camera()


# ============================================================
# JANELA FULLSCREEN
# ============================================================

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.setWindowProperty(
    WINDOW_NAME,
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)


# ============================================================
# ESTADO
# ============================================================

current_point = 0

last_capture_time = 0

capture_cooldown = 0.8


# ============================================================
# LOOP
# ============================================================

try:

    while True:

        # ====================================================
        # CAPTURA
        # ====================================================

        success, frame = cap.read()


        # ====================================================
        # CÂMERA PERDIDA
        # ====================================================

        if not success or frame is None:

            print()
            print("Webcam perdida.")
            print("Tentando reconectar...")
            print()

            cap.release()

            cap = connect_camera()

            continue


        # ====================================================
        # ESPELHAMENTO
        # ====================================================

        frame = cv2.flip(
            frame,
            1
        )


        frame_height, frame_width = frame.shape[:2]


        # ====================================================
        # MEDIA PIPE IMAGE
        # ====================================================

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # IMPORTANTE:
        # Image pertence a mp, não a vision.

        mp_image = mp.Image(

            image_format=mp.ImageFormat.SRGB,

            data=rgb

        )


        timestamp_ms = int(
            time.time() * 1000
        )


        # ====================================================
        # DETECTA MÃO
        # ====================================================

        hand_result = hand_detector.detect_for_video(

            mp_image,

            timestamp_ms

        )


        # ====================================================
        # DETECTA ROSTO
        # ====================================================

        face_result = face_detector.detect_for_video(

            mp_image,

            timestamp_ms

        )


        # ====================================================
        # POSIÇÃO DO INDICADOR
        # ====================================================

        finger_x = None
        finger_y = None


        if hand_result.hand_landmarks:

            # Primeira mão detectada

            hand = hand_result.hand_landmarks[0]


            # Landmark 8 = ponta do indicador

            index_finger = hand[8]


            finger_x = index_finger.x
            finger_y = index_finger.y


        # ====================================================
        # POSIÇÃO DA CABEÇA
        # ====================================================

        head_x = None
        head_y = None


        if face_result.face_landmarks:

            face = face_result.face_landmarks[0]


            # Pontos usados para estimar
            # o centro da cabeça/rosto.

            face_points = [

                face[1],
                face[4],
                face[10],
                face[152]

            ]


            head_x = sum(
                point.x
                for point in face_points
            ) / len(face_points)


            head_y = sum(
                point.y
                for point in face_points
            ) / len(face_points)


        # ====================================================
        # FUNDO
        # ====================================================

        display = frame.copy()


        # ====================================================
        # ALVO ATUAL
        # ====================================================

        if current_point < len(
            CALIBRATION_POINTS
        ):

            point = CALIBRATION_POINTS[
                current_point
            ]


            target_x = int(
                point["x"] *
                frame_width
            )


            target_y = int(
                point["y"] *
                frame_height
            )


            # -----------------------------------------------
            # ALVO
            # -----------------------------------------------

            draw_target(

                display,

                target_x,

                target_y

            )


            # -----------------------------------------------
            # TEXTO
            # -----------------------------------------------

            draw_text(

                display,

                (
                    f"Ponto "
                    f"{current_point + 1}/"
                    f"{len(CALIBRATION_POINTS)}"
                ),

                (30, 45),

                0.8,

                2

            )


            draw_text(

                display,

                point["name"],

                (30, 80),

                0.7,

                2

            )


            draw_text(

                display,

                "Aponte o indicador para o ponto",

                (30, 115),

                0.6,

                2

            )


            draw_text(

                display,

                "ESPACO = registrar",

                (30, 150),

                0.6,

                2

            )


            # -----------------------------------------------
            # INDICADOR DETECTADO
            # -----------------------------------------------

            if finger_x is not None:

                fx = int(
                    finger_x *
                    frame_width
                )


                fy = int(
                    finger_y *
                    frame_height
                )


                cv2.circle(

                    display,

                    (fx, fy),

                    8,

                    (255, 255, 255),

                    2

                )


                # linha entre dedo e alvo

                cv2.line(

                    display,

                    (fx, fy),

                    (target_x, target_y),

                    (255, 255, 255),

                    1

                )


            # -----------------------------------------------
            # CABEÇA
            # -----------------------------------------------

            if head_x is not None:

                hx = int(
                    head_x *
                    frame_width
                )


                hy = int(
                    head_y *
                    frame_height
                )


                cv2.circle(

                    display,

                    (hx, hy),

                    6,

                    (255, 255, 255),

                    -1

                )


        # ====================================================
        # CALIBRAÇÃO CONCLUÍDA
        # ====================================================

        else:

            draw_text(

                display,

                "CALIBRACAO CONCLUIDA",

                (30, 60),

                1.0,

                2

            )


            draw_text(

                display,

                "ENTER = salvar e sair",

                (30, 105),

                0.7,

                2

            )


            draw_text(

                display,

                "ESC = sair",

                (30, 140),

                0.7,

                2

            )


        # ====================================================
        # INFORMAÇÕES
        # ====================================================

        draw_text(

            display,

            (
                f"Camera: "
                f"{frame_width}x{frame_height}"
            ),

            (
                30,
                frame_height - 45
            ),

            0.55,

            1

        )


        draw_text(

            display,

            (
                f"Head-Camera: "
                f"{HEAD_CAMERA_DISTANCE_CM} cm"
            ),

            (
                30,
                frame_height - 20
            ),

            0.55,

            1

        )


        # ====================================================
        # MOSTRA
        # ====================================================

        cv2.imshow(

            WINDOW_NAME,

            display

        )


        # ====================================================
        # TECLADO
        # ====================================================

        key = cv2.waitKey(1) & 0xFF


        # ====================================================
        # ESC
        # ====================================================

        if key == 27:

            print()
            print("Calibração cancelada.")

            break


        # ====================================================
        # ESPAÇO
        # ====================================================

        if key == 32:

            now = time.time()


            if (

                current_point
                <
                len(CALIBRATION_POINTS)

                and

                now - last_capture_time
                >
                capture_cooldown

                and

                finger_x is not None

                and

                finger_y is not None

                and

                head_x is not None

                and

                head_y is not None

            ):

                point = CALIBRATION_POINTS[
                    current_point
                ]


                # =========================================
                # DADOS DO PONTO
                # =========================================

                captured_point = {

                    "name":
                        point["name"],

                    "screen": {

                        "normalized_x":
                            point["x"],

                        "normalized_y":
                            point["y"],

                        "pixel_x":
                            int(
                                point["x"] *
                                SCREEN_WIDTH
                            ),

                        "pixel_y":
                            int(
                                point["y"] *
                                SCREEN_HEIGHT
                            )

                    },

                    "finger": {

                        "x":
                            finger_x,

                        "y":
                            finger_y

                    },

                    "head": {

                        "x":
                            head_x,

                        "y":
                            head_y

                    },

                    "head_camera_distance_cm":
                        HEAD_CAMERA_DISTANCE_CM

                }


                # =========================================
                # SALVA
                # =========================================

                calibration_data.append(

                    captured_point

                )


                save_calibration()


                print()
                print(
                    f"[CALIBRADO] "
                    f"{point['name']}"
                )

                print(
                    f"  Dedo: "
                    f"("
                    f"{finger_x:.4f}, "
                    f"{finger_y:.4f}"
                    f")"
                )

                print(
                    f"  Cabeça: "
                    f"("
                    f"{head_x:.4f}, "
                    f"{head_y:.4f}"
                    f")"
                )

                print(
                    "  JSON atualizado."
                )

                print()


                current_point += 1

                last_capture_time = now


        # ====================================================
        # ENTER
        # ====================================================

        if (

            key == 13

            and

            current_point
            >=
            len(CALIBRATION_POINTS)

        ):

            save_calibration()

            print()
            print("========================================")
            print("       CALIBRAÇÃO CONCLUÍDA")
            print("========================================")
            print()
            print(
                f"Arquivo salvo: {JSON_FILE}"
            )
            print()

            time.sleep(1)

            break


finally:

    # ========================================================
    # LIMPEZA
    # ========================================================

    if cap is not None:

        cap.release()


    cv2.destroyAllWindows()


    hand_detector.close()

    face_detector.close()


    print()
    print("KMouser Calibration encerrado.")