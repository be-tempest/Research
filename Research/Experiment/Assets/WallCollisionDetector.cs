using UnityEngine;

// 壁との衝突を検出するクラス
public class WallCollisionDetector : MonoBehaviour
{
    public TimerController timerController; // TimerControllerの参照

    void Start()
    {
        // TimerControllerの参照を取得
        if (timerController == null)
        {
            timerController = FindObjectOfType<TimerController>();
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        // Playerオブジェクトと衝突した場合
        if (collision.gameObject.CompareTag("Player") && timerController != null)
        {
            timerController.IncrementCollisionCount(); // 衝突回数を増やす
        }
    }
}