<?php
// get the q parameter from GET

// Get the first parameter which is an integer
$value = $_REQUEST["value"];

// Get the second parameter which is a string
$string = $_REQUEST["string"];

//Run the command line for the python script with the value as parameter
$output = shell_exec('/usr/bin/python3 /var/www/html/I2C/pipeline.py '.$value.' '.$string);
?>
