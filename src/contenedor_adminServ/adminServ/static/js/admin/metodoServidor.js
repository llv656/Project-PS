$(document).ready(function(){
        $("#btnCrearServidor").click(function(){
                $("#crear_servidor").val('crear_s');
                return true;
        });
        $("#btnActualizarServidor").click(function(){
                $("#actualizar_servidor").val('actualizar_s');
                return true;
        });
        $("#btnEliminarServidor").click(function(){
                $("#eliminar_servidor").val('eliminar_s');
                return true;
        });
	$("#btnMostrarServidor").click(function(){
                $("#mostrar_servidor").val('mostrar_s');
                return true;
        });
});

