<?php
$nb_step = $_REQUEST["nb_step"];
$orientation = $_REQUEST["orientation"];
$toggler = $_REQUEST["toggler"];


$output = shell_exec('/usr/bin/python3 focus.py '.$nb_step.' '.$orientation.' '.$toggler);
?>
