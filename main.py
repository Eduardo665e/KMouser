import cv2
import time
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

WINDOW_NAME = "KMouser"


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
# FUNÇÃO DE CONEXÃO DA CÂMERA
# ============================================================

def connect_camera():

    while True:

        print("Tentando conectar à webcam...")

        cap = cv2.VideoCapture(CAMERA_INDEX)

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

                print("Webcam detectada!")
                print()

                return cap

            cap.release()

        print("Webcam não disponível.")
        print("Verifique a chave física da câmera.")
        print("Tentando novamente em 2 segundos...")
        print()

        time.sleep(2)


# ============================================================
# CÂMERA
# ============================================================

print()
print("========================================")
print("              KMouser")
print("========================================")
print()

cap = connect_camera()


# ============================================================
# JANELA
# ============================================================

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)


# ============================================================
# CONTROLE DE FPS
# ============================================================

previous_time = time.time()
fps = 0


# ============================================================
# LOOP PRINCIPAL
# ============================================================

try:

    while True:

        # ----------------------------------------------------
        # CAPTURA
        # ----------------------------------------------------

        success, frame = cap.read()


        # ----------------------------------------------------
        # CÂMERA PERDIDA
        # ----------------------------------------------------

        if not success or frame is None:

            print()
            print("Webcam perdida!")
            print("Tentando reconectar...")
            print()

            cap.release()

            cap = connect_camera()

            continue


        # ----------------------------------------------------
        # ESPELHAMENTO
        # ----------------------------------------------------

        frame = cv2.flip(
            frame,
            1
        )


        frame_height, frame_width = frame.shape[:2]


        # ----------------------------------------------------
        # CONVERSÃO
        # ----------------------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )


        timestamp_ms = int(
            time.time() * 1000
        )


        # ====================================================
        # HAND
        # ====================================================

        hand_result = hand_detector.detect_for_video(
            mp_image,
            timestamp_ms
        )


        # ====================================================
        # FACE
        # ====================================================

        face_result = face_detector.detect_for_video(
            mp_image,
            timestamp_ms
        )


        # ====================================================
        # DESENHA MÃOS
        # ====================================================

        if hand_result.hand_landmarks:

            for hand in hand_result.hand_landmarks:

                # --------------------------------------------
                # Conexões da mão
                # --------------------------------------------

                connections = [
                    (0, 1),
                    (1, 2),
                    (2, 3),
                    (3, 4),

                    (0, 5),
                    (5, 6),
                    (6, 7),
                    (7, 8),

                    (0, 9),
                    (9, 10),
                    (10, 11),
                    (11, 12),

                    (0, 13),
                    (13, 14),
                    (14, 15),
                    (15, 16),

                    (0, 17),
                    (17, 18),
                    (18, 19),
                    (19, 20),

                    (5, 9),
                    (9, 13),
                    (13, 17)
                ]


                for start, end in connections:

                    x1 = int(
                        hand[start].x * frame_width
                    )

                    y1 = int(
                        hand[start].y * frame_height
                    )

                    x2 = int(
                        hand[end].x * frame_width
                    )

                    y2 = int(
                        hand[end].y * frame_height
                    )


                    cv2.line(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (255, 255, 255),
                        2
                    )


                # --------------------------------------------
                # Landmarks
                # --------------------------------------------

                for landmark in hand:

                    x = int(
                        landmark.x * frame_width
                    )

                    y = int(
                        landmark.y * frame_height
                    )

                    cv2.circle(
                        frame,
                        (x, y),
                        4,
                        (255, 255, 255),
                        -1
                    )


                # --------------------------------------------
                # Indicador
                # --------------------------------------------

                index = hand[8]

                index_x = int(
                    index.x * frame_width
                )

                index_y = int(
                    index.y * frame_height
                )


                cv2.circle(
                    frame,
                    (index_x, index_y),
                    10,
                    (255, 255, 255),
                    2
                )


        # ====================================================
        # CABEÇA
        # ====================================================

        if face_result.face_landmarks:

            face = face_result.face_landmarks[0]


            points = [
                face[1],
                face[4],
                face[10],
                face[152]
            ]


            head_x = sum(
                point.x for point in points
            ) / len(points)


            head_y = sum(
                point.y for point in points
            ) / len(points)


            head_x = int(
                head_x * frame_width
            )

            head_y = int(
                head_y * frame_height
            )


            # --------------------------------------------
            # Centro da cabeça
            # --------------------------------------------

            cv2.circle(
                frame,
                (head_x, head_y),
                8,
                (255, 255, 255),
                -1
            )


            cv2.line(
                frame,
                (head_x - 20, head_y),
                (head_x + 20, head_y),
                (255, 255, 255),
                2
            )


            cv2.line(
                frame,
                (head_x, head_y - 20),
                (head_x, head_y + 20),
                (255, 255, 255),
                2
            )


        # ====================================================
        # FPS
        # ====================================================

        current_time = time.time()

        delta = current_time - previous_time

        if delta > 0:

            current_fps = 1 / delta

            fps = (
                fps * 0.9
                +
                current_fps * 0.1
            )

        previous_time = current_time


        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )


        cv2.putText(
            frame,
            "KMouser - ESC para sair",
            (20, frame_height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )


        # ====================================================
        # EXIBE
        # ====================================================

        cv2.imshow(
            WINDOW_NAME,
            frame
        )


        # ====================================================
        # TECLADO
        # ====================================================

        key = cv2.waitKey(1) & 0xFF


        if key == 27:

            print()
            print("Encerrando KMouser...")
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

    print("KMouser encerrado.")