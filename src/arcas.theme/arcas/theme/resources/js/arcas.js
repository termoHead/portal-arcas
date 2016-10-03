/**
 * Created with PyCharm.
 * User: Paul
 * Date: 26/09/13
 * Time: 10:58
 * To change this template use File | Settings | File Templates.
 */
jQuery.fn.exists = function(){return this.length>0;}
var solapaActiva
var hojaActiva



var HomeSlider={}
HomeSlider.stepSlide=0

var objFormEnlaceGs = {};
objFormEnlaceGs.tmpValor=""
objFormEnlaceGs.setCampoTmp=function(valor){
    this.tmpValor=valor    
}

function correCarDer(e){    
    e.preventDefault()
    var st=$(".bloqueColeccion").width()+40        
    $("#mask").animate({"margin-left":"+="+st+"px"},"slow")    
}
function correCarIzq(e){    
e.preventDefault()
    var st=$(".bloqueColeccion").width()+40        
    $("#mask").animate({"margin-left":"-="+st+"px"},"slow")    
}

$(document).ready(function() {
    /*carrusel home */
    /*--------------*/
    if($(".bloqueColeccion").length>-1){
        //Step para el slider del HOME
        HomeSlider.stepSlide=$(".bloqueColeccion").width()+40
        if($(".bloqueColeccion").length>1){
            //ACTIVA BOTONES PARA EL SLIDER
            $(".carrD").click(correCarDer)
            $(".carrI").click(correCarIzq)
            
        }
        
    }
    
    var lastSlide=""
    
    if ($(".thumbnails li")[0]){
            hojaActiva=$(".thumbnails li")[0]
    }
    $(".thumbnails li").click(        
        function(ev){
            ev.preventDefault()
            cambiaSlide (ev)
			return false;
        }
    )
    if ($(".listadoRecomendacion")[0]){
            activaSolapas();		
    }
    //if($("#carrusel")){ carruselHome()}
    if($("#buscaTexto")){
            $( ".buscaTexto" ).focus(function() {
                    if($(this).val()=='Buscar en la colección'){
                            $(this).val("")
                    }
            });
            $( ".buscaTexto" ).blur(function() {
                    if($(this).val()=='' || $(this).val()==' ' ){
                            $(this).val("Buscar en la colección")
                    }
            });
    }
    if($(".introExhibicion").length>0){        
          $(".pie a").prepOverlay({subtype:'ajax',filter: '#container .introExhibicion'})
    }
    
    if($("#fieldset-colderecha").length>0){
        initFormColeccion()
    }
    
    
});
function togTexto(ev){

    if($( ev).html().indexOf("(+)")>=0){
       $(ev).html("(-) colapsar texto")
        $(".extraColeccion").show("slow");
    }else{
       $(ev).html("(+) expandir texto")
        $(".extraColeccion").hide("slow");
    }

}
function cambiaSlide(ev){
    /*Cambia slide de la exhibición*/    
	if (ev.currentTarget!=hojaActiva){
		var src=$("img",ev.currentTarget).attr("src")
		var idM=$(ev.currentTarget).attr("class")
		var titulo=$(".titulo",ev.currentTarget).text()
		var texto=$(".cuerpo",ev.currentTarget).text() 		
		$("#fullIMG").remove()
		$(".tituloSlide").text("")
		$(".textoSlide").text("")
		$('<img />').attr({ 'id': 'fullIMG', 'src': src, 'alt':'MyAlt' }).appendTo($('.colImg'));
		$('.pagina .scan').attr("src",src)	
		$(".tituloSlide").text(titulo)
		$(".textoSlide").text(texto)
		$("a",ev.currentTarget).addClass("activo")
		$("a",hojaActiva).removeClass("activo")
        if($("a" , ev.currentTarget).hasClass("externa")){
           $(".pagina a").hide()
        }else{
            $(".pagina a").show()
        }
		hojaActiva=ev.currentTarget
	}
}
function activaSolapas(){
    solapaActiva=$(".listadoRecomendacion .solapa")[0]
    $(".listadoRecomendacion .solapa").click(function(evt){		
		if(evt.currentTarget!=solapaActiva){
			$(solapaActiva).removeClass("activa")
			$(evt.currentTarget).addClass("activa")
			var ventanaCierra=$($("a",solapaActiva).attr("rel"))
			var ventanaAbre=$($("a",evt.currentTarget).attr("rel"))
			$(ventanaCierra).animate({
				opacity: 0.25,
				left: "+=50",
				height: "toggle"
				}, 550, function() {
					$(ventanaAbre).animate({
					opacity: 1,
					left: "+=50",
					height: "toggle"
					}, 550, function() {
					// Animation complete.
					});
				});
			
			solapaActiva=evt.currentTarget
		}
		return false
	})
}

function comodaGaleria(){
    var lW=350;
    var suma=0;
    var buffer=new Array();
    var flag=0;
    var listAr=$(".photoAlbumRow .photoAlbumEntry")
    var valorLinea=0
    var margin=1
    var promedio=0

    for (var elem=0;elem<listAr.length-1;elem++)
    {
        var next=elem+1
		
        if(elem==0){
            suma=$(listAr[elem]).width()
			console.log(suma)
            valorLinea=suma
            buffer[flag]=listAr[elem]
            flag++
        }

        if(next<listAr.length){
            suma+=$(listAr[next]).width()
        }

        if(suma<lW){
		
            buffer[flag]=listAr[next]
            valorLinea+=$(listAr[next]).width()
            flag++
			
        }else{
		
            var gap=(Math.floor((lW-valorLinea)/(buffer.length-1)))-margin
            promedio=gap
			
            for(var ppa=1;ppa<buffer.length;ppa++){
                $(buffer[ppa]).attr("style","margin-left:"+gap+"px");
            }
			
            buffer=new Array()
            buffer[0]=$(listAr[next])
            valorLinea=suma=$(listAr[next]).width()
            flag=1
			
        }
    }

    if(buffer.length>2){
        var gap=(Math.floor((lW-valorLinea)/(buffer.length-1)))-margin
        for(var ppa=1;ppa<buffer.length;ppa++){
            $(buffer[ppa]).attr("style","margin-left:"+gap+"px");
        }
    }else{
        $(buffer[1]).attr("style","margin-left:"+gap+"px");
    }

}

function ocultaCamposEnlaceGS(valor){
    
    if(valor=='1'){
        miHelp='Enlace externo <span class="formHelp">URL hacia un recurso externo. debe incluir el http://</span>'
        $('#formfield-form-widgets-ficha').hide()
        if($("#form-widgets-ficha").attr("value")!=""){
            objFormEnlaceGs.setCampoTmp($("#form-widgets-ficha").attr("value"))
        }
        $("#form-widgets-ficha").attr("value","")
    }else{
        $('#formfield-form-widgets-ficha').show()
        miHelp='Enlace a la fuente primaria  <span class="formHelp">Enlace a la fuente primaria en Greenstone, debe incluir el http://</span>'
        if(objFormEnlaceGs.tmpValor!=""){
           $("#form-widgets-ficha").attr("value",objFormEnlaceGs.tmpValor)
        }
    }
    $('#formfield-form-widgets-urlRemoto label').html(miHelp)
}



function initFormColeccion(){     
    var widgets=["formfield-form-widgets-IColDerSeccion-titulo1","formfield-form-widgets-IColDerSeccion-textoSeccion1","formfield-form-widgets-IColDerSeccion-ria1",
        "formfield-form-widgets-IColDerSeccion-titulo2","formfield-form-widgets-IColDerSeccion-textoSeccion2","formfield-form-widgets-IColDerSeccion-ria2"]
    $(widgets).each(function(i,v){
        $("#"+v).hide()
    })
    $("#form-widgets-IColDerSeccion-tipoSecc1").change(function(e){
        updateFormNum("1",$(this).val())
    })
    $("#form-widgets-IColDerSeccion-tipoSecc2").change(function(e){
        updateFormNum("2",$(this).val())
    })
}
function updateFormNum(numForm,valor){
    var formTitulo=$("#formfield-form-widgets-IColDerSeccion-titulo"+numForm)
    var formTexto=$("#formfield-form-widgets-IColDerSeccion-textoSeccion"+numForm)
    var formRia=$("#formfield-form-widgets-IColDerSeccion-ria"+numForm)
    
    switch(valor) {
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