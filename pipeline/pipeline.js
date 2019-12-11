$(document).ready(function(){

	$( "#send_nb_step" ).click(function() {
		pipeline()
	});
	
	

function pipeline() {
		var value = $("#nb_step").val();
		var orientation = $("#orientation").val();
    
		console.log("pipeline.php?nb_step="+value+"&orientation="+orientation);
		
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", "pipeline.php?nb_step="+value+"&orientation="+orientation, true);
        xmlhttp.send();
	}


});
