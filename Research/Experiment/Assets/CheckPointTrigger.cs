using UnityEngine;

// チェックポイントに入ったときにタイマーをチェックするトリガー
public class CheckPointTrigger : MonoBehaviour
{
    public TimerController timerController; // TimerControllerの参照

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            timerController.CheckTimer(gameObject.name); // タイマーをチェック
        }
    }
}
