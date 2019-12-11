<?php
$volume = $_REQUEST["volume"];
$flowrate = $_REQUEST["flowrate"];
$direction = $_REQUEST["direction"];


$output = shell_exec('/usr/bin/python3 /var/www/html/pipeline/pump.py '.$volume.' '.$flowrate.' '.$direction);
?>
