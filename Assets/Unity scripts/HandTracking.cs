using UnityEngine;

public class HandTracking : MonoBehaviour
{
    public UdpSocket Landmarks;  // Reference to the UdpSocket script
    public GameObject targetObject;  // The 2D object to move based on landmark 8

    // Optional: Adjust scaling factor for both x and y axes
    private float xScaleFactor = 20f;  // Scaling factor for the x-axis to make it move more
    private float yScaleFactor = 20f;  // Scaling factor for the y-axis to make it move more

    void Update()
    {
        // Get the landmark data from UdpSocket
        float[] landmarks = Landmarks.GetLandmarks();

        if (landmarks != null && landmarks.Length >= 2)
        {
            // Check if landmarks array has enough data to access landmark 8 (x and y values)
            float x = landmarks[0] * xScaleFactor;  // Adjust movement on x-axis
            float y = -landmarks[1] * yScaleFactor;  // Adjust movement on y-axis

            // Update the position of the targetObject based on x and y
            targetObject.transform.localPosition = new Vector3(x, y, 0);
        }
        else
        {
            Debug.LogWarning("Landmark data is not available or the array has insufficient elements.");
        }
    }
}
