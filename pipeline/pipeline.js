$(document).ready(function(){

	$( "#focus" ).click(function() {
		focus("ON")
	});
	

	$( "#pump" ).click(function() {	
		pump()
	
	});
	$( "#write" ).click(function() {	
		write()
	
	});


	

	function focus(toggler) {
		var value = $("#nb_step").val();
		var orientation = $("#orientation").val();
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.open("GET", "pipeline/focus.php?nb_step="+value+"&orientation="+orientation+"&toggler="+toggler, true);
		xmlhttp.send();
	}

	function pump() {
		var volume = $("#volume").val();
		var flowrate = $("#flowrate").val();
		var direction = $("#direction").val();
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.open("GET", "pipeline/pump.php?volume="+volume+"&flowrate="+flowrate+"&direction="+direction, true);
		xmlhttp.send();
	}
		
	function write(){

		var xmlhttp = new XMLHttpRequest();
		xmlhttp.open("GET", "pipeline/write.php?txt=ceciestuntexte", true);
		xmlhttp.send();
		
	}

});
