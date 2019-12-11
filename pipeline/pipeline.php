<?php
$nb_step = $_REQUEST["nb_step"];
$orientation = $_REQUEST["orientation"];


$output = shell_exec('/usr/bin/python3 pipeline.py '.$nb_step.' '.$orientation);
?>
