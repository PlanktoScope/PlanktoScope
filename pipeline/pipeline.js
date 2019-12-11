$(document).ready(function(){

	$( "#focus" ).click(function() {
		focus("ON")
	});
	

	$( "#pump" ).click(function() {	
		pump()
	
	});

	

function focus(toggler) {
	var value = $("#nb_step").val();
	var orientation = $("#orientation").val();
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", "focus.php?nb_step="+value+"&orientation="+orientation+"&toggler="+toggler, true);
        xmlhttp.send();
	}

function pump() {
	var volume = $("#volume").val();
	var flowrate = $("#flowrate").val();
	var direction = $("#direction").val();
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", "pump.php?volume="+volume+"&flowrate="+flowrate+"&direction="+direction, true);
        xmlhttp.send();
	}
});
