import cv2
import mediapipe as mp
import socket
import json
import time

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Set up webcam capture
cap = cv2.VideoCapture(0)

# Initialize hands detector
with mp_hands.Hands(
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5) as hands:

    # Set up UDP connection to the server
    udp_ip = '127.0.0.1'  # Server address
    udp_port_send = 8000   # Port to send data to Unity
    udp_port_receive = 8001  # Port to receive data from Unity
    
    # Create the socket for sending data to Unity
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Create the socket for receiving data from Unity
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((udp_ip, udp_port_receive))  # Bind to receive data from Unity

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Convert the BGR frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and detect hands
        results = hands.process(rgb_frame)

        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the position of landmark 8 (tip of the index finger)
                landmark_8 = landmarks.landmark[8]
                x, y = landmark_8.x, landmark_8.y
                z = landmark_8.z  # Optional: you can send this as well if needed

                # Send landmark 8 data to Unity as JSON
                hand_data = {'landmark_8': {'x': x, 'y': y, 'z': z}}
                data_json = json.dumps(hand_data)
                client_socket.sendto(data_json.encode(), (udp_ip, udp_port_send))  # Send data to Unity

                # Print sent data for debugging
                print(f"Sent: {data_json}")

        # Receive data from Unity (or other systems)
        try:
            server_socket.settimeout(1)  # 1 second timeout to prevent blocking indefinitely
            data, addr = server_socket.recvfrom(1024)  # Receive data from Unity
            if data:
                received_data = data.decode()
                print(f"Received from Unity: {received_data}")
        except socket.timeout:
            pass  # No data received, continue with the next loop

        # Display the output frame
        cv2.imshow("Hand Tracking", frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close the socket and release the webcam
    client_socket.close()
    server_socket.close()
    cap.release()
    cv2.destroyAllWindows()
