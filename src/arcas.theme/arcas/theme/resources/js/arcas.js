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
$(document).ready(function() {
    var lastSlide=""
	if ($(".thumbnails li")[0]){
		hojaActiva=$(".thumbnails li")[0]
	}
    $(".thumbnails li").click(
        function(ev){		   		
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

    $("#masColecBoton").click(function(e){
        e.preventDefault()

        if($( e.currentTarget).html().indexOf("(+)")>=0){
           $( e.currentTarget).html("(-) colapsar texto")
        }else{
           $( e.currentTarget).html("(+) expandir texto")
        }
        $("#extraColeccion").toggle("slow");

    })
});

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

