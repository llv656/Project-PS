$(document).ready(function(){
/*	$.ajax({url: '/informacion_servidor/', success: function(result){
		$('#monitor_seccion').html(result);
	}});*/
	$('#monitor_seccion').load('/informacion_servidor/')
});

