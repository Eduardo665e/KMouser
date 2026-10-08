import cv2
import json
import time
import mediapipe as mp
import numpy as np


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CAMERA_INDEX = 0

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

CALIBRATION_FILE = "calibration.json"

MODEL_HAND = "models/hand_landmarker.task"
MODEL_FACE = "models/face_landmarker.task"

WINDOW_NAME = "KMouser - Cursor Test"

RECONNECT_DELAY = 2.0

# Quanto menor, mais suave
# Quanto maior, mais rápido responde
SMOOTHING = 0.25


# ============================================================
# MEDIAPIPE
# ============================================================

BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode

HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions


# ============================================================
# CARREGAR CALIBRAÇÃO
# ============================================================

def load_calibration():

    print("Carregando calibração...")

    with open(CALIBRATION_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    screen_width = data["screen"]["width"]
    screen_height = data["screen"]["height"]

    points = {
        point["name"]: point
        for point in data["points"]
    }

    required_points = [
        "TOP_LEFT",
        "TOP_RIGHT",
        "CENTER",
        "BOTTOM_LEFT",
        "BOTTOM_RIGHT"
    ]

    for name in required_points:

        if name not in points:

            raise RuntimeError(
                f"Ponto de calibração ausente: {name}"
            )

    print("Calibração carregada.")
    print(
        f"Monitor: "
        f"{screen_width}x{screen_height}"
    )
    print()

    return data


# ============================================================
# CRIAR HOMOGRAFIA
# ============================================================

def create_homography(calibration):

    points = {
        point["name"]: point
        for point in calibration["points"]
    }

    # --------------------------------------------------------
    # Agora usamos a posição do dedo RELATIVA À CABEÇA.
    #
    # Isso significa:
    #
    # relative_x = finger_x - head_x
    # relative_y = finger_y - head_y
    #
    # Assim a cabeça funciona como origem.
    # --------------------------------------------------------

    source = []

    calibration_order = [
        "TOP_LEFT",
        "TOP_RIGHT",
        "BOTTOM_RIGHT",
        "BOTTOM_LEFT"
    ]

    for name in calibration_order:

        point = points[name]

        finger_x = point["finger"]["x"]
        finger_y = point["finger"]["y"]

        head_x = point["head"]["x"]
        head_y = point["head"]["y"]

        relative_x = finger_x - head_x
        relative_y = finger_y - head_y

        source.append([
            relative_x,
            relative_y
        ])

    source = np.array(
        source,
        dtype=np.float32
    )

    # --------------------------------------------------------
    # DESTINO = PIXELS DO MONITOR
    # --------------------------------------------------------

    destination = np.array([

        [
            points["TOP_LEFT"]["screen"]["pixel_x"],
            points["TOP_LEFT"]["screen"]["pixel_y"]
        ],

        [
            points["TOP_RIGHT"]["screen"]["pixel_x"],
            points["TOP_RIGHT"]["screen"]["pixel_y"]
        ],

        [
            points["BOTTOM_RIGHT"]["screen"]["pixel_x"],
            points["BOTTOM_RIGHT"]["screen"]["pixel_y"]
        ],

        [
            points["BOTTOM_LEFT"]["screen"]["pixel_x"],
            points["BOTTOM_LEFT"]["screen"]["pixel_y"]
        ]

    ], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(
        source,
        destination
    )

    print("Homografia criada usando posição relativa à cabeça.")
    print()

    # --------------------------------------------------------
    # MOSTRAR OS PONTOS UTILIZADOS
    # --------------------------------------------------------

    print("Pontos de calibração:")
    print()

    for i, name in enumerate(calibration_order):

        print(
            f"{name:15} "
            f"REL=({source[i][0]: .4f}, "
            f"{source[i][1]: .4f}) "
            f"-> "
            f"SCREEN=({destination[i][0]:.0f}, "
            f"{destination[i][1]:.0f})"
        )

    print()

    return matrix


# ============================================================
# TRANSFORMAR DEDO -> TELA
# ============================================================

def finger_to_screen(
    relative_x,
    relative_y,
    matrix
):

    point = np.array(
        [[[relative_x, relative_y]]],
        dtype=np.float32
    )

    transformed = cv2.perspectiveTransform(
        point,
        matrix
    )

    screen_x = float(
        transformed[0][0][0]
    )

    screen_y = float(
        transformed[0][0][1]
    )

    return screen_x, screen_y


# ============================================================
# SUAVIZAÇÃO
# ============================================================

def smooth_position(
    current_x,
    current_y,
    previous_x,
    previous_y
):

    if (
        previous_x is None
        or previous_y is None
    ):

        return current_x, current_y

    new_x = (
        previous_x
        + (
            current_x - previous_x
        ) * SMOOTHING
    )

    new_y = (
        previous_y
        + (
            current_y - previous_y
        ) * SMOOTHING
    )

    return new_x, new_y


# ============================================================
# CONECTAR À WEBCAM
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

            if (
                success
                and frame is not None
            ):

                print("Webcam detectada!")
                print()

                return cap

            cap.release()

        print("Webcam não disponível.")
        print(
            "Verifique a câmera."
        )
        print(
            f"Tentando novamente em "
            f"{RECONNECT_DELAY:.1f} segundos..."
        )
        print()

        time.sleep(
            RECONNECT_DELAY
        )


# ============================================================
# TEXTO
# ============================================================

def draw_text(
    frame,
    text,
    x,
    y,
    scale=0.6,
    thickness=2
):

    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("========================================")
    print("       KMouser - Cursor Test")
    print("========================================")
    print()

    # ========================================================
    # CALIBRAÇÃO
    # ========================================================

    calibration = load_calibration()

    screen_width = calibration["screen"]["width"]
    screen_height = calibration["screen"]["height"]

    homography = create_homography(
        calibration
    )

    # ========================================================
    # MEDIAPIPE - MÃO
    # ========================================================

    hand_options = HandLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=MODEL_HAND
        ),
        running_mode=VisionRunningMode.IMAGE,
        num_hands=2
    )

    # ========================================================
    # MEDIAPIPE - ROSTO
    # ========================================================

    face_options = FaceLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=MODEL_FACE
        ),
        running_mode=VisionRunningMode.IMAGE,
        num_faces=1
    )

    hand_landmarker = (
        HandLandmarker.create_from_options(
            hand_options
        )
    )

    face_landmarker = (
        FaceLandmarker.create_from_options(
            face_options
        )
    )

    # ========================================================
    # WEBCAM
    # ========================================================

    cap = connect_camera()

    previous_cursor_x = None
    previous_cursor_y = None

    last_time = time.time()

    fps = 0.0

    try:

        while True:

            # =================================================
            # CAPTURA
            # =================================================

            success, frame = cap.read()

            if (
                not success
                or frame is None
            ):

                print()
                print("Webcam perdida!")

                cap.release()

                cap = connect_camera()

                previous_cursor_x = None
                previous_cursor_y = None

                continue

            # =================================================
            # ESPELHAR
            # =================================================

            frame = cv2.flip(
                frame,
                1
            )

            # =================================================
            # RGB
            # =================================================

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            # =================================================
            # DETECTAR MÃO
            # =================================================

            hand_result = (
                hand_landmarker.detect(
                    mp_image
                )
            )

            # =================================================
            # DETECTAR CABEÇA
            # =================================================

            face_result = (
                face_landmarker.detect(
                    mp_image
                )
            )

            # =================================================
            # VARIÁVEIS
            # =================================================

            head_x = None
            head_y = None

            finger_x = None
            finger_y = None

            # =================================================
            # CABEÇA
            # =================================================

            if face_result.face_landmarks:

                face = (
                    face_result.face_landmarks[0]
                )

                # Pontos utilizados na calibração
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

                # ---------------------------------------------
                # DESENHAR CABEÇA
                # ---------------------------------------------

                hx = int(
                    head_x *
                    frame.shape[1]
                )

                hy = int(
                    head_y *
                    frame.shape[0]
                )

                cv2.circle(
                    frame,
                    (hx, hy),
                    8,
                    (255, 0, 255),
                    -1
                )

                draw_text(
                    frame,
                    "HEAD",
                    hx + 12,
                    hy,
                    0.45,
                    1
                )

            # =================================================
            # MÃO
            # =================================================

            if hand_result.hand_landmarks:

                # Primeira mão detectada
                hand = (
                    hand_result.hand_landmarks[0]
                )

                # ---------------------------------------------
                # LANDMARKS
                # ---------------------------------------------

                for landmark in hand:

                    px = int(
                        landmark.x *
                        frame.shape[1]
                    )

                    py = int(
                        landmark.y *
                        frame.shape[0]
                    )

                    cv2.circle(
                        frame,
                        (px, py),
                        3,
                        (0, 255, 0),
                        -1
                    )

                # ---------------------------------------------
                # CONEXÕES DA MÃO
                # ---------------------------------------------

                connections = [

                    (0, 1),
                    (1, 2),
                    (2, 3),
                    (3, 4),

                    (0, 5),
                    (5, 6),
                    (6, 7),
                    (7, 8),

                    (5, 9),
                    (9, 10),
                    (10, 11),
                    (11, 12),

                    (9, 13),
                    (13, 14),
                    (14, 15),
                    (15, 16),

                    (13, 17),
                    (17, 18),
                    (18, 19),
                    (19, 20),

                    (0, 17)

                ]

                for a, b in connections:

                    ax = int(
                        hand[a].x *
                        frame.shape[1]
                    )

                    ay = int(
                        hand[a].y *
                        frame.shape[0]
                    )

                    bx = int(
                        hand[b].x *
                        frame.shape[1]
                    )

                    by = int(
                        hand[b].y *
                        frame.shape[0]
                    )

                    cv2.line(
                        frame,
                        (ax, ay),
                        (bx, by),
                        (0, 255, 0),
                        2
                    )

                # ---------------------------------------------
                # INDICADOR
                # ---------------------------------------------

                index_finger = hand[8]

                finger_x = index_finger.x
                finger_y = index_finger.y

                fx = int(
                    finger_x *
                    frame.shape[1]
                )

                fy = int(
                    finger_y *
                    frame.shape[0]
                )

                cv2.circle(
                    frame,
                    (fx, fy),
                    10,
                    (0, 0, 255),
                    2
                )

                cv2.circle(
                    frame,
                    (fx, fy),
                    4,
                    (0, 0, 255),
                    -1
                )

                draw_text(
                    frame,
                    "INDEX",
                    fx + 12,
                    fy,
                    0.45,
                    1
                )

            # =================================================
            # CALCULAR POSIÇÃO RELATIVA
            # =================================================

            relative_x = None
            relative_y = None

            if (
                finger_x is not None
                and finger_y is not None
                and head_x is not None
                and head_y is not None
            ):

                relative_x = (
                    finger_x - head_x
                )

                relative_y = (
                    finger_y - head_y
                )

            # =================================================
            # CURSOR VIRTUAL
            # =================================================

            cursor_x = None
            cursor_y = None

            if (
                relative_x is not None
                and relative_y is not None
            ):

                cursor_x, cursor_y = (
                    finger_to_screen(
                        relative_x,
                        relative_y,
                        homography
                    )
                )

                # ---------------------------------------------
                # LIMITAR À TELA
                # ---------------------------------------------

                cursor_x = max(
                    0,
                    min(
                        screen_width - 1,
                        cursor_x
                    )
                )

                cursor_y = max(
                    0,
                    min(
                        screen_height - 1,
                        cursor_y
                    )
                )

                # ---------------------------------------------
                # SUAVIZAÇÃO
                # ---------------------------------------------

                cursor_x, cursor_y = (
                    smooth_position(
                        cursor_x,
                        cursor_y,
                        previous_cursor_x,
                        previous_cursor_y
                    )
                )

                previous_cursor_x = cursor_x
                previous_cursor_y = cursor_y

            # =================================================
            # MINI MONITOR
            # =================================================

            monitor_width = 260
            monitor_height = 146

            monitor_x = (
                frame.shape[1]
                - monitor_width
                - 20
            )

            monitor_y = 30

            # Moldura
            cv2.rectangle(
                frame,
                (
                    monitor_x,
                    monitor_y
                ),
                (
                    monitor_x + monitor_width,
                    monitor_y + monitor_height
                ),
                (255, 255, 255),
                2
            )

            draw_text(
                frame,
                "MONITOR VIRTUAL",
                monitor_x,
                monitor_y - 8,
                0.45,
                1
            )

            # =================================================
            # CURSOR NO MINI MONITOR
            # =================================================

            if (
                cursor_x is not None
                and cursor_y is not None
            ):

                mini_x = int(
                    monitor_x
                    + (
                        cursor_x /
                        screen_width
                    ) *
                    monitor_width
                )

                mini_y = int(
                    monitor_y
                    + (
                        cursor_y /
                        screen_height
                    ) *
                    monitor_height
                )

                # Cursor
                cv2.circle(
                    frame,
                    (mini_x, mini_y),
                    9,
                    (0, 0, 255),
                    -1
                )

                cv2.circle(
                    frame,
                    (mini_x, mini_y),
                    15,
                    (0, 0, 255),
                    2
                )

            # =================================================
            # LINHA DEDO -> CURSOR
            # =================================================

            if (
                finger_x is not None
                and cursor_x is not None
            ):

                fx = int(
                    finger_x *
                    frame.shape[1]
                )

                fy = int(
                    finger_y *
                    frame.shape[0]
                )

                if (
                    cursor_x is not None
                    and cursor_y is not None
                ):

                    mini_x = int(
                        monitor_x
                        + (
                            cursor_x /
                            screen_width
                        ) *
                        monitor_width
                    )

                    mini_y = int(
                        monitor_y
                        + (
                            cursor_y /
                            screen_height
                        ) *
                        monitor_height
                    )

                    cv2.line(
                        frame,
                        (fx, fy),
                        (mini_x, mini_y),
                        (0, 0, 255),
                        1
                    )

            # =================================================
            # FPS
            # =================================================

            current_time = time.time()

            delta = (
                current_time
                - last_time
            )

            if delta > 0:

                instant_fps = (
                    1.0 / delta
                )

                fps = (
                    fps * 0.9
                    + instant_fps * 0.1
                )

            last_time = current_time

            # =================================================
            # HUD
            # =================================================

            draw_text(
                frame,
                "KMouser Cursor Test",
                15,
                30,
                0.7,
                2
            )

            draw_text(
                frame,
                f"FPS: {fps:.1f}",
                15,
                58,
                0.55,
                1
            )

            # -------------------------------------------------
            # COORDENADAS DO DEDO
            # -------------------------------------------------

            if finger_x is not None:

                draw_text(
                    frame,
                    f"FINGER: "
                    f"{finger_x:.3f}, "
                    f"{finger_y:.3f}",
                    15,
                    88,
                    0.48,
                    1
                )

            # -------------------------------------------------
            # COORDENADAS DA CABEÇA
            # -------------------------------------------------

            if head_x is not None:

                draw_text(
                    frame,
                    f"HEAD: "
                    f"{head_x:.3f}, "
                    f"{head_y:.3f}",
                    15,
                    115,
                    0.48,
                    1
                )

            # -------------------------------------------------
            # RELATIVO
            # -------------------------------------------------

            if relative_x is not None:

                draw_text(
                    frame,
                    f"RELATIVE: "
                    f"{relative_x:+.3f}, "
                    f"{relative_y:+.3f}",
                    15,
                    142,
                    0.48,
                    1
                )

            # -------------------------------------------------
            # TELA
            # -------------------------------------------------

            if cursor_x is not None:

                draw_text(
                    frame,
                    f"SCREEN: "
                    f"{cursor_x:.0f}, "
                    f"{cursor_y:.0f}",
                    15,
                    169,
                    0.55,
                    1
                )

            else:

                draw_text(
                    frame,
                    "SCREEN: aguardando...",
                    15,
                    169,
                    0.55,
                    1
                )

            # =================================================
            # INSTRUÇÃO
            # =================================================

            draw_text(
                frame,
                "ESC = sair",
                15,
                frame.shape[0] - 20,
                0.5,
                1
            )

            # =================================================
            # MOSTRAR
            # =================================================

            cv2.imshow(
                WINDOW_NAME,
                frame
            )

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == 27:
                break

    finally:

        print()
        print(
            "Encerrando "
            "KMouser Cursor Test..."
        )

        cap.release()

        hand_landmarker.close()
        face_landmarker.close()

        cv2.destroyAllWindows()

        print("Encerrado.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()