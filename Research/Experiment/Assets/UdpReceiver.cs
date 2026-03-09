using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

// UDP受信クラス
public class UdpReceiver : MonoBehaviour
{
    private UdpClient udpClient;
    private IPEndPoint remoteEndPoint;
    private string jsonData = "";

    public bool IsWalking { get; private set; } = false; // Walking 
    public int LookPoint { get; private set; } = 5; // LookPoint

    void Start()
    {
        int listenPort = 5005; // Python側と同じポート番号を指定
        udpClient = new UdpClient(listenPort);
        remoteEndPoint = new IPEndPoint(IPAddress.Any, listenPort);

        // 非同期でUDP受信を開始
        udpClient.BeginReceive(ReceiveCallback, null);
    }

    private void ReceiveCallback(IAsyncResult ar)
    {
        try
        {
            byte[] receivedData = udpClient.EndReceive(ar, ref remoteEndPoint);
            jsonData = Encoding.UTF8.GetString(receivedData);

            // JSONデータを解析
            ParseReceivedData(jsonData);

            // 次のUDP受信を開始
            udpClient.BeginReceive(ReceiveCallback, null);
        }
        catch (Exception ex)
        {
            Debug.LogError($"UDP Receive Error: {ex.Message}");
        }
    }

    private void ParseReceivedData(string jsonData)
    {
        try
        {
            // JSONデータを解析
            var receivedObject = JsonUtility.FromJson<UdpData>(jsonData);
            IsWalking = receivedObject.walking;
            LookPoint = receivedObject.LookPoint;
        }
        catch (Exception ex)
        {
            Debug.LogError($"JSON Parse Error: {ex.Message}");
        }
    }

    void OnDestroy()
    {
        udpClient?.Close();
    }

    // JSONデータの構造を定義
    [Serializable]
    private class UdpData
    {
        public bool walking;
        public int LookPoint;
    }
}