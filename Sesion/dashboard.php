<?php
session_start();
if (!isset($_SESSION['username'])) {
    header("Location: login.php");
    exit;
}

include 'config.php';

$username = $_SESSION['username'];
$sql = "SELECT phone FROM users WHERE username = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $username);
$stmt->execute();
$result = $stmt->get_result();
$user = $result->fetch_assoc();

echo "Welcome, " . $_SESSION['username'] . "!<br>";
echo "Your phone number is: " . $user['phone'] . "<br>";
echo "<a href='logout.php'>Logout</a>";
?>