/**
 * Created with PyCharm.
 * User: Paul
 * Date: 26/09/13
 * Time: 10:58
 * To change this template use File | Settings | File Templates.
 */
jQuery.fn.exists = function(){return this.length>0;}


$(document).ready(function() {
    var lastSlide=""
    $(".colThum li").click(
        function(ev){
            ev.preventDefault()
            cambiaSlide (ev)
        }
    )
    if ($(".galeriaBox").exists()) {
//
    }


});
function cambiaSlide(ev){
    /*Cambia slide de la exhibición*/
    var src=$("img",ev.currentTarget).attr("src")
    var idM=$(ev.currentTarget).attr("class")
    var titulo=$(".titulo",ev.currentTarget).text()
    var texto=$(".cuerpo",ev.currentTarget).text()
    //console.log(idM.substr(idM.indexOf("_")+1,100))

    $("#fullIMG").remove()
    $(".tituloSlide").text("")
    $(".textoSlide").text("")
    $('<img />').attr({ 'id': 'fullIMG', 'src': src, 'alt':'MyAlt' }).appendTo($('.colImg'));
    $(".tituloSlide").text(titulo)
    $(".textoSlide").text(texto)
}

function comodaGaleria(){
    var lW=350;
    var suma=0;
    var buffer=new Array();
    var flag=0;
    var listAr=$(".marcoImgs img")
    var valorLinea=0
    var margin=1
    var promedio=0
    for (var elem=0;elem<listAr.length-1;elem++)
    {
        var next=elem+1
        if(elem==0){
            suma=$(listAr[elem]).width()
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