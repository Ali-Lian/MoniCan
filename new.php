<?php
// 資料庫連線設定
$config = include('config.php');

$host = $config['host'];
$user = $config['user'];
$password = $config['password'];
$database = $config['dbname'];

$conn = new mysqli($servername, $username, $password, $dbname);

// 檢查連線是否成功
if ($conn->connect_error) {
    die("連線失敗: " . $conn->connect_error);
}

// 模擬裝置編號
$device_id = "5";

// 獲取現在的日期時間
$start_time = new DateTime();

// 生成10筆資料
for ($i = 41; $i < 50; $i++) {
    // 模擬高度範圍在0至100之間
    $distance = round(mt_rand(0, 10000) / 100, 2);
    
    // 模擬重量範圍在0至100之間
    $weight = round(mt_rand(0, 10000) / 100, 2);
    
    // 產生隨機T或F值
    $target = (mt_rand(0, 1) === 1) ? 'T' : 'F';
    
    // 設定每分鐘產生一筆資料
    $current_time = $start_time->add(new DateInterval('PT1M'));
    
    // 格式化日期時間
    $formatted_time = $current_time->format("Y-m-d H:i:s");
    
    // 準備 SQL 語句
    $sql = "INSERT INTO record (recordID, timeStamp, distance, weight, trashCanID) VALUES ('$i', '$formatted_time', '$distance', '$weight', '$device_id')";
    
    // 執行 SQL 語句
    if ($conn->query($sql) !== TRUE) {
        echo "資料插入失敗: " . $conn->error;
    }
}

// 關閉資料庫連線
$conn->close();
?>