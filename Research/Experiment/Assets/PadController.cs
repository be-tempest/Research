using UnityEngine;

// パッドでプレイヤーを操作するクラス
public class PadController : MonoBehaviour
{
    public Camera playerCamera; // プレイヤーのカメラ
    public float moveSpeed = 2.0f; // 移動速度
    public float rotationSpeed = 2.0f; // 回転速度
    public float maxVerticalAngle = 50.0f; // 垂直角度の最大値

    private float currentVerticalAngle = 0.0f; // 現在の垂直角度
    private float currentHorizontalAngle = 0.0f; // 現在の水平角度

    void Update()
    {
        if (playerCamera == null) return;

        // キーボード入力による移動
        HandleMovement();

        // パッド入力による視線操作
        HandlePadLook();
    }

    private void HandleMovement()
    {
        // `W`キーで前進
        if (Input.GetKey(KeyCode.W))
        {
            Vector3 forwardDirection = playerCamera.transform.forward;
            forwardDirection.y = 0; // 垂直方向を無視
            forwardDirection.Normalize();
            transform.Translate(forwardDirection * moveSpeed * Time.deltaTime, Space.World);
        }
    }

    private void HandlePadLook()
    {
        // パッド入力による視線操作
        float horizontalInput = 0.0f;
        float verticalInput = 0.0f;

        if (Input.GetKey(KeyCode.RightArrow))
        {
            horizontalInput = rotationSpeed;
        }
        else if (Input.GetKey(KeyCode.LeftArrow))
        {
            horizontalInput = -rotationSpeed;
        }

        if (Input.GetKey(KeyCode.UpArrow))
        {
            verticalInput = rotationSpeed;
        }
        else if (Input.GetKey(KeyCode.DownArrow))
        {
            verticalInput = -rotationSpeed;
        }

        // 水平角度の更新 (360度以内に制限)
        currentHorizontalAngle += horizontalInput;

        // 垂直角度の更新 (最大値と最小値を制限)
        currentVerticalAngle -= verticalInput;
        currentVerticalAngle = Mathf.Clamp(currentVerticalAngle, -maxVerticalAngle, maxVerticalAngle);

        // カメラの角度を更新
        playerCamera.transform.localEulerAngles = new Vector3(currentVerticalAngle, currentHorizontalAngle, 0);
    }
}
