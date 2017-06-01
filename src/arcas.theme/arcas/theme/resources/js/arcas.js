/**
 * Created with PyCharm.
 * User: Paul
 * Date: 26/09/13
 * Time: 10:58
 * To change this template use File | Settings | File Templates.
 */
jQuery.fn.exists = function () {
	return this.length > 0;
}
var solapaActiva
var hojaActiva
var HomeSlider = {}
var objFormEnlaceGs = {};
HomeSlider.stepSlide = 0

objFormEnlaceGs.tmpValor = ""
objFormEnlaceGs.setCampoTmp = function (valor) {
	this.tmpValor = valor
}

function enviaLoco() {
	$('#form').submit()
}

function getQueryParams(qs) {
    //devuelve los paramatreos de la url
    qs = qs.split('+').join(' ');

    var params = {},
        tokens,
        re = /[?&]?([^=]+)=([^&]*)/g;

    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }
    return params;
}

var EDITGS=(function () { 
    var my = {},
    objIds=0,
	privateVariable = 1;        
    function init(){
        agregaIdioma("#formfield-form-widgets-f_idioma")
        agregaIdioma("#formfield-form-widgets-s_lenguaiso")
    }
    
    
    function agregaIdioma(selector){
        var boton=$(document.createElement("div"))
        var enlace=$(document.createElement("a"))
        var holdimg=$(document.createElement("span"))
        var idBoton="agregaOp"+objIds

        holdimg.attr('class',"holdimage")
        enlace.attr("id",idBoton)
        enlace.attr("class","option")
        enlace.attr("href","#")        
        enlace.attr("style","margin-top:12px")
        enlace.text('agregar idioma [+]')
        enlace.append(holdimg)        
        //boton.attr("class","option")
        boton.attr("id","masoption"+objIds)
        boton.attr("style","width:400px;margin-top:65px")
        boton.append(enlace)
        $(boton).insertAfter(selector)
        
        $("#"+idBoton).click(function(e){            
            e.preventDefault()
            
            var n=addOption(selector.split("-")[selector.split("-").length-1],selector)
            
            $(selector).append(n)
            
            //$(this).parent().parent().height('200')
            
        })
        
        objIds++
    }

    function addOption(nombreLista){
        var nuevoID ="nuevoOption" + privateVariable;
        var elemento= $(document.createElement("span"))
        var borra   = $(document.createElement("a"))
        var imput   = $(document.createElement("input"))
        var lid='form-widgets-'+nombreLista+'-'+(100+privateVariable)
        
        var chk=$('<input id="'+lid+'" class="checkbox-widget list-field" name="form.widgets.'+nombreLista+':list" type="checkbox" checked="checked"  />')
        
        var help    = $(document.createElement("label"))
        
        imput.attr("rel",lid)
        help.text(" borrar")
        borra.text("[X]")
        borra.attr("href","#")

        elemento.attr("id",nuevoID)
        elemento.attr("class","option")
        elemento.attr("style","margin-right:15px")
        chk.hide()
        elemento.append(chk)
        elemento.append(imput)
        elemento.append(help)
        elemento.append(borra)
        
        imput.blur(function(e){
            var valor=$(this).attr('value')
            var idd=$(this).attr('rel')
            
            $("#"+idd).prop("value",valor)
        })
        
        borra.click(function(e){
            e.preventDefault();
            privateVariable-- ;
            if(privateVariable==1){$(this).parent().parent().height('120');}
            $(this).parent().remove();
        })

        privateVariable++;
        return elemento;

    }
    my.inicia=function(){        
        init()
    }
    return my
})()



var MOD_GSEDIT = (function () {      
    var qq = getQueryParams(document.location.search);    
    $(".formControls #form-buttons-cancel").click(function(e){
        e.preventDefault()
        setTimeout(500,function(){window.close()})
    })
    setTimeout(500,function(){
    
    if(qq.coleccion!=undefined){
        var inp=$(document.createElement("input"))
        inp.attr('id','#form-widgets-coleccion')
        $('option[value="puig"]').attr('selected', 'selected')}            
        $( "#form-widgets-coleccion" ).replaceWith(inp);
        $('#from-widgets-coleccion').parent().append("<h2>Coleccion "+qq.coleccion+"</h2>")            
    })
	var camposEdicion = ["f_fechaCreacion", "f_lugarCreacion", "f_descFisica", "f_dimensiones", "f_idioma", "f_naturaleza", "f_alcance", "f_anotacion", "f_ruta"]
	var grupos = ["fieldsetlegend-datos", "fieldsetlegend-serie","fieldsetlegend-subserie","fieldsetlegend-item","fieldset-datos","fieldset-serie",
        "fieldsetlegend-subserie","fieldset-item"]

	var infoMetaItem = {
		'f_fechaCreacion' : 'ae.itemcoberturatemporal',
		'f_lugarCreacion' : 'bi.lugar',
		'f_descFisica' : 'ae.itemdescripcionfisica',
		'f_dimensiones' : 'ae.itemdimension',
		'f_idioma' : 'ae.itemlenguaiso',
		'f_naturaleza' : 'ae.itemnaturaleza',
		'f_alcance' : 'ae.itemalcance',
		'f_anotacion' : 'bi.anotacionitem',
		'f_ruta' : 'bi.ruta'
	}

	var infoMetadatosSerie = {
		'ae.serietitulo' : 's_titulo',
		'ae.seriecoberturatemporal' : 's_temporal',
		'ae.fileextension' : 's_extension',
		'ae.seriedescripcionfisica' : 's_caracteristicas',
		'ae.serieautor' : 's_autor',
		'ae.seriealcance' : 's_alcance',
		'ae.serielenguaiso' : 's_lenguaiso'
	}

	var infoMetadatosSubSerie = {
		'ae.subserietitulo' : 'sub_titulo',
		'ae.subserieautor' : 'sub_alcance',
		'ae.subserielenguaiso' : 'sub_anotacion'
	}

	var infoMetadatosItem = {
		'ae.itemcoberturatemporal' : 'f_fechaCreacion',
		'bi.lugar' : 'f_lugarCreacion',
		'ae.itemdescripcionfisica' : 'f_descFisica',
		'ae.itemdimension' : 'f_dimensiones',
		'ae.itemlenguaiso' : 'f_idioma',
		'ae.itemnaturaleza' : 'f_naturaleza',
		'ae.itemalcance' : 'f_alcance',
		'bi.anotacionitem' : 'f_anotacion',
		'bi.ruta' : 'f_ruta'
	}
	var my = {},
	privateVariable = 1;
        
    function dameColeccionElegida(){            
            if($("#form-widgets-coleccion option:selected").length>0){
                colec = $("#form-widgets-coleccion option:selected").attr("value")    
            }else{
                colec = $("#form-widgets-coleccion-1").attr("value")
            }
            return colec
        }
	function i() {
		var subser = "false";
        
       
		if ($("#form-buttons-guardar").length == 0) {
			ocultaCamposEdit()
		}
		$("#fieldset-datos").show()
		$("#form-widgets-serie").change(function (e) {
                        var colec = dameColeccionElegida()
			var valor = $('#form-widgets-serie option:selected').attr('value')                         
                        buscaFuentejson('/json_gs', valor, colec)
		})
		$("#form-widgets-coleccion").change(function () {
                    var colec = dameColeccionElegida()
			$("#form-widgets-obra option").remove()
			buscaSeriejson("/json_gs", colec)
		})
		$("#form-widgets-subserie").change(function () {
                    var colec = dameColeccionElegida()
			$("#form-widgets-obra option").remove()
			var subserie = $("#form-widgets-subserie option:selected").attr("value")
			buscaSubSeriejson(colec, subserie)
		})
		$("#form-widgets-obra").change(function () {
                    var colec = dameColeccionElegida()
			var valor = $('#form-widgets-serie option:selected').attr('value')
			var ruta = $("#form-widgets-obra option:selected").attr("value")
			if ($("#form-widgets-obra option:selected").length > 0) {
                            subser = "true"
			}
			buscaMetadatajson("/json_gs", valor, colec, ruta, subser)
		})
        
	}
	function ocultaCamposEdit() {
		for (var a = 1; a < grupos.length; a++) {
			$("#" + grupos[a]).hide()
			//$("#" + grupos[a + 3]).hide()
		}
		for (var a = 0; a < camposEdicion.length; a++) {
			$("#formfield-form-widgets-" + camposEdicion[a]).hide()
		}
	}
	function muestraCamposEdit() {        
		for (var a = 1; a < Math.floor(grupos.length/2); a++) {
			$("#" + grupos[a]).css('display', 'inline-block')
		}
		for (var a = 0; a < camposEdicion.length; a++) {
			$("#formfield-form-widgets-" + camposEdicion[a]).show()
		}
            $("#fieldsetlegend-item").click()
            setTimeout(function(){$("#fieldset-item").show("slow")},100)
	}

	function buscaSubSeriejson(colec, subserie) {
		$.ajax({
			dataType : "json",
			url : "/arcas/json_gs",
			data : {
				"coleccion" : colec,
				"subserie" : subserie
			},
		}).done(function (data) {
			$("#form-widgets-obra option").remove()
			var fa = 0
				op = $('<option id="form-widgets-obra-novalue" value="--NOVALUE--">Sin valor</option>')
				$("#form-widgets-obra").append(op);

			total = $(data).length;
			$.each(data, function (key, val) {
				op = $('<option value="' + val.value + '">' + val.title + '</option>')
					fa++
					$("#form-widgets-obra").append(op);
			})
			return data            
		})
	}

	function buscaSeriejson(url, colec) {
		$.ajax({
			dataType : "json",
			url : "/arcas/json_gs",
			data : {
				"series" : colec
			},
		}).done(function (data) {
			$("#form-widgets-serie option").remove()
			var fa = 0

				op = $('<option id="form-widgets-serie-novalue" value="--NOVALUE--">Sin valor</option>')
				$("#form-widgets-serie").append(op);

			total = $(data).length;

			$.each(data, function (key, val) {
                console.log(val.value==true)
				if (val.value!=true) {
					op = $('<option value="' + val.value + '">' + val.title + '</option>')
						fa++
						$("#form-widgets-serie").append(op);
				} else {
					if (val.subserie == false) {
						$("#formfield-form-widgets-subserie").hide()
					} else {
						$("#formfield-form-widgets-subserie").show()
					}
				}

			})
			return data
		})
	}

	function buscaFuenteSubJson() {}
	function buscaFuentejson(url, serie, coleccion) {
		$.ajax({
			dataType : "json",
			url : "/arcas/json_gs",
			data : {
				"docs" : serie,
				"coleccion" : coleccion
			},
		}).done(function (data) {
			$("#form-widgets-subserie option").remove()
			$("#form-widgets-obra option").remove()
			if (data[0].value == "tieneSubSerie") {
				op = $('<option id="form-widgets-subserie-novalue" value="--NOVALUE--">Sin valor</option>')
					$("#form-widgets-subserie").append(op);
				$.each(data, function (key, val) {
					if (val.value != "tieneSubSerie" && val.value != "undefined") {
						var op = $('<option value="' + val.value + '">' + val.title + '</option>')
							$("#form-widgets-subserie").append(op);
					}
				})
			} else {
				op = $('<option id="form-widgets-obra-novalue" value="--NOVALUE--">Sin valor</option>')
					$("#form-widgets-obra").append(op);
				$.each(data, function (key, val) {
					var op = $('<option value="' + val.value + '">' + val.title + '</option>')
						$("#form-widgets-obra").append(op);
				})
			}
			return data
		})
	}

	function buscaMetadatajson(url, serie, coleccion, ruta, subser) {
		$.ajax({
			dataType : "json",
			url : "/arcas/json_gs",
			data : {
				"docs" : serie,
				"coleccion" : coleccion,
				"ruta" : ruta,
				"subserie" : subser
			},
		}).done(function (data) {
			$.each(data, function (key, val) {
				if (key == "serieMetadata") {
					$.each(val, function (k, v) {
						var tmpN = Object.keys(v)[0]
							$("#form-widgets-" + infoMetadatosSerie[tmpN]).attr("value", v[tmpN])
					})
				}
				if (key == "itemMetadata") {
					$.each(val, function (k, v) {
						var tmpN = Object.keys(v)[0]
							$("#form-widgets-" + infoMetadatosItem[tmpN]).attr("value", v[tmpN])
					})
				}
				if (key == "subserieMetadata") {
					$.each(val, function (k, v) {
						var tmpN = Object.keys(v)[0]
							$("#form-widgets-" + infoMetadatosSubSerie[tmpN]).attr("value", v[tmpN])
					})
				}
				$(val.value).attr("value", val.title)
			})
            //setTimeout(muestraCamposEdit, 500)
            setTimeout(function(){
                $("#form").submit()
            },500)
                return data
            });
	}
    
   
	my.moduleProperty = 1;
	my.inicia = function () {
		i()
        
	};
	return my
})()
function correCarDer(e) {
	e.preventDefault()
	var st = $(".bloqueColeccion").width() + 40
		$("#mask").animate({
			"margin-left" : "+=" + st + "px"
		}, "slow")
}
function correCarIzq(e) {
	e.preventDefault()
	var st = $(".bloqueColeccion").width() + 40
		$("#mask").animate({
			"margin-left" : "-=" + st + "px"
		}, "slow")
}

$(document).ready(function () {
	/*carrusel home */
	/*--------------*/
	if ($(".bloqueColeccion").length > -1) {
		//Step para el slider del HOME
		HomeSlider.stepSlide = $(".bloqueColeccion").width() + 40
			if ($(".bloqueColeccion").length > 1) {
				//ACTIVA BOTONES PARA EL SLIDER
				$(".carrD").click(correCarDer)
				$(".carrI").click(correCarIzq)
			}
	}

	var lastSlide = ""

		if ($(".thumbnails li")[0]) {
			hojaActiva = $(".thumbnails li")[0]
		}
		$(".thumbnails li").click(
			function (ev) {
			ev.preventDefault()
			cambiaSlide(ev)
			return false;
		})
		if ($(".listadoRecomendacion")[0]) {
			activaSolapas();
		}
		//if($("#carrusel")){ carruselHome()}
		if ($("#buscaTexto")) {
			$(".buscaTexto").focus(function () {
				if ($(this).val() == 'Buscar en la colección') {
					$(this).val("")
				}
			});
			$(".buscaTexto").blur(function () {
				if ($(this).val() == '' || $(this).val() == ' ') {
					$(this).val("Buscar en la colección")
				}
			});
		}
		if ($(".introExhibicion").length > 0) {
			$(".pie a").prepOverlay({
				subtype : 'ajax',
				filter : '#container .introExhibicion'
			})
		}

		if ($("#fieldset-colderecha").length > 0) {
			initFormColeccion()
		}

		if ($(".template-editgs").length > 0) {
			//estoy en el formulario edicion greenstone
			var objEGS = MOD_GSEDIT
			objEGS.inicia()
		}
		if ($(".template-edititem").length > 0 || $(".template-nuevoitemgs").length > 0 ) {
			//estoy en el formulario edicion greenstone            
			var objEGS = EDITGS
			objEGS.inicia()
		}
        
		
        /*IMagenes de la Galeria en una Coleccion */
        $('.photoAlbumEntry a').prepOverlay({
            subtype: 'image',
            urlmatch: '/image_view_fullscreen$',
            urlreplace: '_preview',
            width:'70%',
        });
        
        $("input[name*='s1.query']").focus(foco) 
        $("input[name*='s1.query']").blur(esfumado) 
        
        
        if($(".template-edititem").length>0){
            $("#fieldsetlegend-seleccia3n-de-atem-serie").parent().hide()
        }
        
        /*agrega QUIK ADD*/
        
        //agregaChekbox()
        
});
function foco(e){    
    var valor=$(this).attr("value")
    if (valor=="Buscar en las colecciones"){
        $(this).attr("value","")
    }
}
function esfumado(e){
    
    var valor=$(this).attr("value")
    if (valor==""){
        $(this).attr("value","Buscar en las colecciones")
    }
}
function togTexto(ev) {

	if ($(ev).html().indexOf("(+)") >= 0) {
		$(ev).html("(-) colapsar texto")
		$(".extraColeccion").show("slow");
	} else {
		$(ev).html("(+) expandir texto")
		$(".extraColeccion").hide("slow");
	}

}
function cambiaSlide(ev) {
	/*Cambia slide de la exhibición*/
        console.log($(".cuerpo", ev.currentTarget).clone().html())
        
	if (ev.currentTarget != hojaActiva) {
            $(".texto").text("")
            var src = $("img", ev.currentTarget).attr("src")
                        
			var idM = $(ev.currentTarget).attr("class")                        
            var texto = $(".cuerpo", ev.currentTarget).clone()
                        
			var titulo = $(".titulo", ev.currentTarget).text()
            var nuevoTitulo=$('<h3>'+titulo+'</h3>')
             
            
            $("#contenido .texto").append(nuevoTitulo)	
            $("#contenido .texto").append(texto.html())	
			
			$("#fullIMG").remove()						
			$('<img />').attr({
				'id' : 'fullIMG',
				'src' : src,
				'alt' : 'MyAlt'
			}).appendTo($('.colImg'));
		$('.pagina .scan').attr("src", src)
                
                
			
		$("a", ev.currentTarget).addClass("activo")
		$("a", hojaActiva).removeClass("activo")
		if ($("a", ev.currentTarget).hasClass("externa")) {
			$(".pagina a").hide()
		} else {
			$(".pagina a").show()
		}
		hojaActiva = ev.currentTarget
	}
}
function activaSolapas() {
	solapaActiva = $(".listadoRecomendacion .solapa")[0]
		$(".listadoRecomendacion .solapa").click(function (evt) {
			if (evt.currentTarget != solapaActiva) {
				$(solapaActiva).removeClass("activa")
				$(evt.currentTarget).addClass("activa")
				var ventanaCierra = $($("a", solapaActiva).attr("rel"))
					var ventanaAbre = $($("a", evt.currentTarget).attr("rel"))
					$(ventanaCierra).animate({
						opacity : 0.25,
						left : "+=50",
						height : "toggle"
					}, 550, function () {
						$(ventanaAbre).animate({
							opacity : 1,
							left : "+=50",
							height : "toggle"
						}, 550, function () {
							// Animation complete.
						});
					});

				solapaActiva = evt.currentTarget
			}
			return false
		})
}
function comodaGaleria() {
	var lW = 350;
	var suma = 0;
	var buffer = new Array();
	var flag = 0;
	var listAr = $(".photoAlbumRow .photoAlbumEntry")
		var valorLinea = 0
		var margin = 1
		var promedio = 0

		for (var elem = 0; elem < listAr.length - 1; elem++) {
			var next = elem + 1

				if (elem == 0) {
					suma = $(listAr[elem]).width()
						console.log(suma)
						valorLinea = suma
						buffer[flag] = listAr[elem]
						flag++
				}

				if (next < listAr.length) {
					suma += $(listAr[next]).width()
				}

				if (suma < lW) {

					buffer[flag] = listAr[next]
						valorLinea += $(listAr[next]).width()
						flag++

				} else {

					var gap = (Math.floor((lW - valorLinea) / (buffer.length - 1))) - margin
					promedio = gap

						for (var ppa = 1; ppa < buffer.length; ppa++) {
							$(buffer[ppa]).attr("style", "margin-left:" + gap + "px");
						}

						buffer = new Array()
						buffer[0] = $(listAr[next])
						valorLinea = suma = $(listAr[next]).width()
						flag = 1

				}
		}

		if (buffer.length > 2) {
			var gap = (Math.floor((lW - valorLinea) / (buffer.length - 1))) - margin
			for (var ppa = 1; ppa < buffer.length; ppa++) {
				$(buffer[ppa]).attr("style", "margin-left:" + gap + "px");
			}
		} else {
			$(buffer[1]).attr("style", "margin-left:" + gap + "px");
		}
		

}
function ocultaCamposEnlaceGS(valor) {
	if (valor == '1') {
		miHelp = 'Enlace externo <span class="formHelp">URL hacia un recurso externo. debe incluir el http://</span>'
			$('#formfield-form-widgets-ficha').hide()
			if ($("#form-widgets-ficha").attr("value") != "") {
				objFormEnlaceGs.setCampoTmp($("#form-widgets-ficha").attr("value"))
			}
			$("#form-widgets-ficha").attr("value", "")
	} else {
		$('#formfield-form-widgets-ficha').show()
		miHelp = 'Enlace a la fuente primaria  <span class="formHelp">Enlace a la fuente primaria en Greenstone, debe incluir el http://</span>'
			if (objFormEnlaceGs.tmpValor != "") {
				$("#form-widgets-ficha").attr("value", objFormEnlaceGs.tmpValor)
			}
	}
	$('#formfield-form-widgets-urlRemoto label').html(miHelp)
}
function initFormColeccion() {
	var widgets = ["formfield-form-widgets-IColDerSeccion-titulo1", "formfield-form-widgets-IColDerSeccion-textoSeccion1", "formfield-form-widgets-IColDerSeccion-ria1",
		"formfield-form-widgets-IColDerSeccion-titulo2", "formfield-form-widgets-IColDerSeccion-textoSeccion2", "formfield-form-widgets-IColDerSeccion-ria2"]
	$(widgets).each(function (i, v) {
		$("#" + v).hide()
	})
	$("#form-widgets-IColDerSeccion-tipoSecc1").change(function (e) {
		updateFormNum("1", $(this).val())
	})
	$("#form-widgets-IColDerSeccion-tipoSecc2").change(function (e) {
		updateFormNum("2", $(this).val())
	})
}
function updateFormNum(numForm, valor) {
	var formTitulo = $("#formfield-form-widgets-IColDerSeccion-titulo" + numForm)
		var formTexto = $("#formfield-form-widgets-IColDerSeccion-textoSeccion" + numForm)
		var formRia = $("#formfield-form-widgets-IColDerSeccion-ria" + numForm)

		switch (valor) {
		case "texto":
			$(formRia).hide()
			$(formTexto).show()
			$(formTitulo).show()
			break;
		case "video":
			$(formRia).show()
			$(formTexto).hide()
			$(formTitulo).show()
			break;
		case "imagen":
			$(formRia).show()
			$(formTexto).hide()
			$(formTitulo).hide()
			break;
		case "galeria":
			$(formRia).hide()
			$(formTexto).hide()
			$(formTitulo).hide()
			break;
		}

}

/*QUIK EDIT*/

function agregaChekbox(){
var nee=$(document.createElement('a'))
nee.attr("href","http://arcasdev.fahce.unlp.edu.ar:9090/arcas/portada/colecciones/manuel-puig/manuel-puig_estudios/++add++arcas.sugerencia")
nee.attr("id","sugerenciAdd")
nee.text("Agregar Item")
$("#enlace0").prepend(nee)
$("#enlace0 .item").each(
  function(){
    var nea=$(document.createElement('input'))
    nea.attr("type","checkbox")
    $(this).prepend(nea)
  })

    $("#sugerenciAdd").prepOverlay({
	subtype : 'ajax',
        filter: '#content > *',
        closeselector:'#form-buttons-cancel',
    })

}


