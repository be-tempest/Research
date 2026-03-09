using UnityEngine;

// ゴールポイントに入ったときにタイマーを停止するトリガー
public class GoalPointTrigger : MonoBehaviour
{
    public TimerController timerController; // TimerControllerの参照

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            // Debug.Log("ゴールポイントに到達しました");
            timerController.StopTimer(); // タイマーを停止
        }
    }
}