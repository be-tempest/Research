using UnityEngine;

// 実験手法に基づいてプレイヤーを操作するクラス
public class PlayerController : MonoBehaviour
{
    public UdpReceiver udpReceiver; // UDPReceiverクラスの参照
    public Camera playerCamera; // プレイヤーのカメラ
    public float moveSpeed = 2.0f; // 移動速度
    public float rotationSpeedV = 0.1f; // 1フレームあたりの垂直回転速度
    public float rotationSpeedH = 0.1f; // 1フレームあたりの水平回転速度
    public float maxVerticalAngle = 50.0f; // 垂直角度の最大値

    private float currentVerticalAngle = 0.0f; // 現在の垂直角度
    private float currentHorizontalAngle = 0.0f; // 現在の水平角度

    private bool canMove = false; // 移動可能かどうか
    private float startTime; // 開始時間

    void Start()
    {
        // 開始時間の設定
        startTime = Time.time;
    }

    void Update()
    {
        if (udpReceiver == null || playerCamera == null) return;

        // 10秒経過したら canMove を true に設定
        if (!canMove && Time.time - startTime >= 10.0f)
        {
            canMove = true;
            Debug.Log("10秒経過しました。移動を開始します。");
        }

        // 移動可能でない場合、処理を終了
        if (!canMove) return;

        // LookPointの値に応じて視線を操作
        float verticalChange = 0.0f;
        float horizontalChange = 0.0f;

        switch (udpReceiver.LookPoint)
        {
            case 1: //　左上
                verticalChange = rotationSpeedV;
                horizontalChange = -rotationSpeedH;
                break;
            case 2: // 上
                verticalChange = rotationSpeedV;
                break;
            case 3: // 右上
                verticalChange = rotationSpeedV;
                horizontalChange = rotationSpeedH;
                break;
            case 4: // 左
                horizontalChange = -rotationSpeedH;
                break;
            case 5: // 真ん中
                break;
            case 6: // 右
                horizontalChange = rotationSpeedH;
                break;
            case 7: // 左下
                verticalChange = -rotationSpeedV;
                horizontalChange = -rotationSpeedH;
                break;
            case 8: // 下
                verticalChange = -rotationSpeedV;
                break;
            case 9: // 右下
                verticalChange = -rotationSpeedV;
                horizontalChange = rotationSpeedH;
                break;
        }

        // 水平角度の更新 (360度以内に制限)
        currentHorizontalAngle += horizontalChange;
        currentHorizontalAngle = currentHorizontalAngle % 360.0f; // 360度以内に制限

        // 垂直角度の更新 (最大値と最小値を制限)
        currentVerticalAngle -= verticalChange;
        currentVerticalAngle = Mathf.Clamp(currentVerticalAngle, -maxVerticalAngle, maxVerticalAngle);

        // カメラの角度を更新
        playerCamera.transform.localEulerAngles = new Vector3(currentVerticalAngle, currentHorizontalAngle, 0);

        // 移動処理
        if (udpReceiver.IsWalking)
        {
            Vector3 forwardDirection = playerCamera.transform.forward;
            forwardDirection.y = 0; // 水平方向のみを考慮
            forwardDirection.Normalize();
            transform.Translate(forwardDirection * moveSpeed * Time.deltaTime, Space.World);
        }
    }
}
