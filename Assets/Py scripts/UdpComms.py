import socket
import threading

class UdpComms():
    def __init__(self, udpIP, portTX, portRX, enableRX=False, suppressWarnings=True):
        """
        Constructor to initialize UDP communication
        """
        self.udpIP = udpIP
        self.udpSendPort = portTX
        self.udpRcvPort = portRX
        self.enableRX = enableRX
        self.suppressWarnings = suppressWarnings
        self.isDataReceived = False
        self.dataRX = None

        # Create the UDP socket for communication
        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udpSock.bind((udpIP, portRX))

        if enableRX:
            # Create a separate thread for receiving data
            self.rxThread = threading.Thread(target=self.ReadUdpThreadFunc, daemon=True)
            self.rxThread.start()

    def __del__(self):
        self.CloseSocket()

    def CloseSocket(self):
        self.udpSock.close()

    def SendData(self, strToSend):
        self.udpSock.sendto(bytes(strToSend, 'utf-8'), (self.udpIP, self.udpSendPort))

    def ReceiveData(self):
        if not self.enableRX:
            raise ValueError("Attempting to receive data without enabling RX.")
        data = None
        try:
            data, _ = self.udpSock.recvfrom(1024)
            data = data.decode('utf-8')
        except Exception as e:
            print(f"Error receiving data: {e}")
        return data

    def ReadUdpThreadFunc(self):
        """
        This function continuously checks for incoming data and stores it when received.
        """
        self.isDataReceived = False
        while True:
            data = self.ReceiveData()
            if data:
                self.dataRX = data
                self.isDataReceived = True

    def ReadReceivedData(self):
        """
        This function returns data received by the thread if available.
        """
        if self.isDataReceived:
            self.isDataReceived = False
            return self.dataRX
        return None
