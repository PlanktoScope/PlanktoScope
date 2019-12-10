function pipeline() {
		var value = $("#value").val();
		var string = $("#string").text();
    
		console.log("pipeline.php?value="+value+"&string="+string);
		
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", "pipeline.php?value="+value+"&string="+string, true);
        xmlhttp.send();
	}
