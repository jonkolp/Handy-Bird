using System;
using System.Collections;
using System.Net.Sockets;
using UnityEngine;

/// <summary>
/// Controls the Flappy Bird character by receiving real-time gesture control signals
/// over a TCP socket from the Python computer vision backend (MP.py).
/// </summary>
[RequireComponent(typeof(Rigidbody2D))]
public class Bird : MonoBehaviour
{
    [Header("Movement & Physics")]
    [Tooltip("Upward velocity applied when flapping.")]
    public float jumpForce = 5.0f;

    [Tooltip("Constant horizontal forward velocity.")]
    public float forwardSpeed = 1.0f;

    [Tooltip("Minimum time (in seconds) between jumps to prevent rapid fluttering.")]
    [SerializeField] private float jumpCooldown = 0.2f;

    [Tooltip("Reset downward velocity before jumping to ensure responsive mid-fall flaps.")]
    [SerializeField] private bool resetVerticalVelocityOnJump = true;

    [Tooltip("If true, pauses horizontal speed while the jump flag is active (assignment behavior).")]
    [SerializeField] private bool stopForwardOnJump = false;

    [Header("Network Configuration")]
    [Tooltip("IP address of the Python MediaPipe TCP server.")]
    [SerializeField] private string host = "127.0.0.1";

    [Tooltip("Port of the Python MediaPipe TCP server.")]
    [SerializeField] private int port = 65432;

    [Tooltip("Interval (in seconds) to retry connecting if the server is offline.")]
    [SerializeField] private float reconnectInterval = 2.0f;

    [Tooltip("Toggle verbose debug messages in the Unity Console.")]
    [SerializeField] private bool enableDebugLogging = false;

    // Networking references
    private TcpClient client;
    private NetworkStream stream;
    private readonly byte[] buffer = new byte[1024];
    private bool isConnected = false;
    private Coroutine reconnectCoroutine;

    // Component references & state tracking
    private Rigidbody2D rb;
    private float lastJumpTime = -1.0f;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    private void Start()
    {
        reconnectCoroutine = StartCoroutine(AutoConnectLoop());
    }

    private void Update()
    {
        if (!isConnected || stream == null)
        {
            return;
        }

        try
        {
            // Drain the socket buffer to process only the freshest gesture packet,
            // preventing accumulated frame lag when framerates fluctuate.
            bool receivedData = false;
            byte latestFlag = 0;

            while (stream.DataAvailable)
            {
                int bytesRead = stream.Read(buffer, 0, buffer.Length);
                if (bytesRead > 0)
                {
                    latestFlag = buffer[bytesRead - 1];
                    receivedData = true;
                }
            }

            if (receivedData)
            {
                ProcessGesture(latestFlag);
            }
        }
        catch (Exception ex)
        {
            LogWarning($"Network stream error: {ex.Message}. Attempting reconnect...");
            DisconnectFromServer();
            if (isActiveAndEnabled && reconnectCoroutine == null)
            {
                reconnectCoroutine = StartCoroutine(AutoConnectLoop());
            }
        }
    }

    /// <summary>
    /// Processes the received gesture flag (1 = Jump, 0 = Cruise/Glide).
    /// </summary>
    /// <param name="jumpFlag">Flag byte received from Python.</param>
    private void ProcessGesture(byte jumpFlag)
    {
        if (enableDebugLogging)
        {
            Debug.Log($"[Bird] Received gesture flag: {jumpFlag}");
        }

        if (jumpFlag == 1)
        {
            ExecuteJump();

            float targetX = stopForwardOnJump ? 0f : forwardSpeed;
            rb.velocity = new Vector2(targetX, rb.velocity.y);
        }
        else
        {
            rb.velocity = new Vector2(forwardSpeed, rb.velocity.y);
        }
    }

    /// <summary>
    /// Applies an upward impulse to make the bird flap.
    /// </summary>
    public void Jump()
    {
        ExecuteJump();
    }

    private void ExecuteJump()
    {
        if (Time.time - lastJumpTime < jumpCooldown)
        {
            return;
        }

        lastJumpTime = Time.time;

        if (resetVerticalVelocityOnJump)
        {
            // Consistent flap response even during steep falls
            rb.velocity = new Vector2(rb.velocity.x, jumpForce);
        }
        else
        {
            rb.AddForce(Vector2.up * jumpForce, ForceMode2D.Impulse);
        }

        if (enableDebugLogging)
        {
            Debug.Log("[Bird] Jump executed!");
        }
    }

    /// <summary>
    /// Continually attempts to connect to the Python server at a set interval.
    /// </summary>
    private IEnumerator AutoConnectLoop()
    {
        while (!isConnected)
        {
            TryConnect();
            if (!isConnected)
            {
                yield return new WaitForSeconds(reconnectInterval);
            }
        }
        reconnectCoroutine = null;
    }

    private void TryConnect()
    {
        try
        {
            client = new TcpClient();
            var result = client.BeginConnect(host, port, null, null);
            bool success = result.AsyncWaitHandle.WaitOne(TimeSpan.FromSeconds(1));

            if (!success || !client.Connected)
            {
                client.Close();
                client = null;
                return;
            }

            client.EndConnect(result);
            stream = client.GetStream();
            isConnected = true;
            Debug.Log($"[Bird] Successfully connected to Python server at {host}:{port}");
        }
        catch (Exception ex)
        {
            DisconnectFromServer();
            if (enableDebugLogging)
            {
                Debug.LogWarning($"[Bird] Connection attempt failed: {ex.Message}");
            }
        }
    }

    private void DisconnectFromServer()
    {
        isConnected = false;

        try
        {
            stream?.Close();
            stream = null;
        }
        catch { }

        try
        {
            client?.Close();
            client = null;
        }
        catch { }
    }

    private void OnDisable()
    {
        if (reconnectCoroutine != null)
        {
            StopCoroutine(reconnectCoroutine);
            reconnectCoroutine = null;
        }
        DisconnectFromServer();
    }

    private void OnApplicationQuit()
    {
        DisconnectFromServer();
    }

    private void LogWarning(string message)
    {
        if (enableDebugLogging)
        {
            Debug.LogWarning($"[Bird] {message}");
        }
    }
}
