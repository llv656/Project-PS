$(document).ready(function(){
        $("#btnCrearAdmin").click(function(){
                $("#crear_admin").val('crear');
                return true;
        });
	$("#btnActualizarAdmin").click(function(){
                $("#actualizar_admin").val('actualizar');
                return true;
        });
	$("#btnEliminarAdmin").click(function(){
                $("#eliminar_admin").val('eliminar');
                return true;
        });
	$("#btnMostrarAdmin").click(function(){
                $("#mostrar_admin").val('mostrar');
                return true;
        });
});
