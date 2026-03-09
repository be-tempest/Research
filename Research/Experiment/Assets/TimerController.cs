using UnityEngine;
using UnityEngine.UI;

// タイマーを管理するクラス
public class TimerController : MonoBehaviour
{
    public Text timerText; // タイマー表示用のUIテキスト
    private float startTime; // タイマー開始時間
    private float elapsedTime; // 経過時間
    private bool isTiming = false; // タイマーが動作中かどうか
    private int collisionCount = 0; // 衝突回数

    void Start()
    {
        // タイマーを初期化
        UpdateTimerDisplay(0);
    }

    // タイマーを開始
    public void StartTimer()
    {
        if (!isTiming)
        {
            startTime = Time.time;
            isTiming = true;
            collisionCount = 0; // 衝突回数を初期化
            Debug.Log("タイマーを開始しました");
        }
    }

    // タイマーをチェック
    public void CheckTimer(string objectName)
    {
        if (isTiming)
        {
            Debug.Log($"CheckPoint: {objectName}, Time: {elapsedTime:F2}, Collision: {collisionCount}");
        }
    }

    // タイマーを停止
    public void StopTimer()
    {
        if (isTiming)
        {
            // float elapsedTime = Time.time - startTime;
            isTiming = false;
            Debug.Log($"タイマーを停止しました。Time: {elapsedTime:F2}, Collision: {collisionCount}");

            // タイマーのUIを更新
            UpdateTimerDisplay(elapsedTime);
        }
    }

    // 衝突回数を増やす
    public void IncrementCollisionCount()
    {
        if (isTiming)
        {
            collisionCount++;
        }
    }

    void Update()
    {
        // タイマーが動作中の場合、経過時間を更新
        if (isTiming)
        {
            elapsedTime = Time.time - startTime;
            UpdateTimerDisplay(elapsedTime);
        }

        // Rキーが押されたらタイマーをリセット
        if (Input.GetKeyDown(KeyCode.R))
        {
            ResetTimer();
        }
    }

    void UpdateTimerDisplay(float time)
    {
        if (timerText != null)
        {
            timerText.text = $"Time: {time:F2} Collision: {collisionCount}";
        }
    }

    public void ResetTimer()
    {
        // タイマーを初期化
        isTiming = false;
        startTime = 0;
        collisionCount = 0; // 衝突回数を初期化
        Debug.Log("タイマーをリセットしました");

        // タイマーのUIを更新
        UpdateTimerDisplay(0);
    }
}