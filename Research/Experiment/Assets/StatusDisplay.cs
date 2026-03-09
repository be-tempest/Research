using UnityEngine;
using UnityEngine.UI;

// ステータスを表示するクラス
public class StatusDisplay : MonoBehaviour
{
    public UdpReceiver udpReceiver; // UDPReceiverからデータを取得するための参照
    public Text statusText; // ステータステキストを表示するためのUIText

    void Update()
    {
        if (udpReceiver != null)
        {
            // UDPReceiverからデータを取得してステータステキストを更新
            statusText.text = $"Walking: {udpReceiver.IsWalking}, LookPoint: {udpReceiver.LookPoint}";
        }
    }
}