using UnityEngine;
using System.Collections;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

public class UdpSocket : MonoBehaviour
{
    [HideInInspector] public bool isTxStarted = false;

    [SerializeField] string IP = "127.0.0.1"; // Localhost IP
    [SerializeField] int rxPort = 8000; // Port to receive data from Python
    [SerializeField] int txPort = 8001; // Port to send data to Python

    private float[] landmarks; // To store the landmark positions

    // Get the landmarks array (only x and y for landmark 8)
    public float[] GetLandmarks()
    {
        return landmarks;
    }

    void Awake()
    {
        // Create remote endpoint (to send data to Python)
        IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Parse(IP), txPort);

        // Create local UDP client to listen on the receiving port
        client = new UdpClient(rxPort);

        // Start the receiving thread
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();

        // Initialize the connection
        print("UDP Comms Initialized");
    }

    private UdpClient client;
    private Thread receiveThread;

    // Method to receive data from Python
    private void ReceiveData()
    {
        while (true)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = client.Receive(ref anyIP);
                string receivedData = Encoding.UTF8.GetString(data);

                // Process received data (assume it's a JSON-like format with x, y, z for landmark 8)
                ProcessInput(receivedData);
            }
            catch (Exception err)
            {
                print(err.ToString());
            }
        }
    }

    // Process the input received from Python
    private void ProcessInput(string input)
    {
        try
        {
            // Manually parse the received data
            // Example received string: {"landmark_8": {"x": 0.5, "y": 0.7, "z": 0.1}}

            // Extract x, y, z values from the string
            int startX = input.IndexOf("\"x\":") + 4;
            int startY = input.IndexOf("\"y\":") + 4;
            int startZ = input.IndexOf("\"z\":") + 4;

            // Extract values and parse them as floats
            float x = float.Parse(input.Substring(startX, input.IndexOf(",", startX) - startX).Trim());
            float y = float.Parse(input.Substring(startY, input.IndexOf(",", startY) - startY).Trim());
            float z = float.Parse(input.Substring(startZ, input.IndexOf("}", startZ) - startZ).Trim());

            // Store the landmark values (x and y for landmark 8)
            landmarks = new float[2] { x, y };

            // Optionally, log the values to console for debugging
            Debug.Log("Received Landmark 8 - X: " + x + ", Y: " + y);
        }
        catch (Exception e)
        {
            Debug.LogError("Error processing input: " + e.Message);
        }
    }

    // Prevent crashes - close clients and threads properly
    void OnDisable()
    {
        if (receiveThread != null)
            receiveThread.Abort();

        client.Close();
    }
}
