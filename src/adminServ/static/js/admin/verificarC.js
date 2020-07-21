$(document).ready(function(){
	function validarContra(contra) {
		var mayus = new RegExp("^(?=.*[A-Z])");
		var especial = new RegExp("^(?=.*[-_!@#$%&*])");
		var number = new RegExp("^(?=.*[0-9])");
		var minus = new RegExp("^(?=.*[a-z])");

		if(mayus.test(contra) && especial.test(contra) && number.test(contra) && minus.test(contra)) {
			return true;
		}
		return false;
	}

	$("#btnCrearAdmin").click(function(){
		var contra = $("#passwordAdmin").val();
		if (contra.length < 10) {
			$("#errorAdminR").css("display", "block");
			$("#errorAdminR").html("<STRONG>ERROR: Revise las politicas para la creacion de contraseñas </STRONG>");
			return false;
		}
		if (!validarContra(contra)) {
			$("#errorAdminR").css("display", "block");
			$("#errorAdminR").html("<STRONG>ERROR: Revise las politicas para la creacion de contraseñas </STRONG>");
			return false;
		}
	});
});
