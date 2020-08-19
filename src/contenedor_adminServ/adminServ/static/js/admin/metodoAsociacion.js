$(document).ready(function(){
        $("#btnCrearAsociacion").click(function(){
                $("#crear_asociacion").val('crear_as');
                return true;
        });
        $("#btnEliminarAsociacion").click(function(){
                $("#eliminar_asociacion").val('eliminar_as');
                return true;
        });
	$("#btnMostrarAsociacion").click(function(){
                $("#mostrar_asociacion").val('mostrar_as');
                return true;
        });
});
