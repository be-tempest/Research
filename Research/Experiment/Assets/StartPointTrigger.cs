using UnityEngine;

//　スタートポイントのトリガー
public class StartPointTrigger : MonoBehaviour
{
    public TimerController timerController; // TimerControllerの参照

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            timerController.StartTimer(); // タイマーを開始
        }
    }
}