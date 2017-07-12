#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Paul'
import urllib2
import xml.etree.ElementTree as ET
import os
import sys
import time
from arcas.content.config import infoMetadatosSerie as FinfoMetadatosSerie
from arcas.content.config import infoMetadatoSubSerie as FinfoMetadatoSubSerie
from arcas.content.config import infoMetaItem as FinfoMetaItem
from arcas.content.config import itemTitles,subSerieTitles,serieTitle
from xml.dom import minidom


class FSManager(object):
    """
        Abre el archivo y lo guarda en miXml
        gsx=FSManager()
        fileOk=gsx.openF(ruta, coleccion)
        if fileOk==False:
            print "error:%s"%gsx.erromMsj
            return
        fileXml=gsx.miXml

    """

    erromMsj=""
    xmlFileBase  ='/usr/local/Greenstone3/web/sites/localsite/collect/'
    xmlFileResto ='/import/co.1/se.1/su.1/ar.1/it.1/'
    xmlFileName='metadata.xml'
    miXml=""


    def openF(self,ruta,coll):
        """ruta: es ruta al archivo greenston, desde el import,
        coll: es id de coleccion"""
        ruta=self.xmlFileBase+coll+"/"+ruta
        result=self.openFile(ruta)

        return result

    def openFile(self, ruta):

        try:
            xmlFile = ET.parse(ruta)
            self.miXml=xmlFile
            return True

        except ET.ParseError:
            print("failure")
            print("last successful: {0}".format(last))
            self.erromMsj={"error":u"Error de parseo"}

        except:
            print("catastrophic failure")
            self.erromMsj={"error":u"No se encontró el archivo"}

        return False

    def parseXmlFileMetadata(self,colec,ruta):
        """Dada la ruta y la coleccion, abre un archivo XML y parsea los metadatos devolviendolos en un diccionario.
        Lo uso en editItem"""

        dicc={}
        miFile=self.openF(ruta,colec)
        metaUsados=[]

        if miFile:
            metas=self.miXml.find("./FileSet/Description").findall(".//Metadata")

            for elem in metas:
                metaN=elem.attrib["name"]


                if metaN not in metaUsados:
                    metaUsados.append(metaN)
                    print len(elem.text)
                    dicc[metaN]=elem.text
                else:
                    #si metaN está cargado,
                    #me fijo si ya está convertido en lista

                    if isinstance(dicc[metaN],list):
                        dicc[metaN].append(elem.text)
                    else:
                        #transformo el str en una lista, para cargar multiples valores
                        tmpp=[dicc[metaN],elem.text,]
                        dicc[metaN]=tmpp




                #tmp=[]
                #for mm in elem:
                #    tmp.append(mm.text)
                #dicc.update({elem.attrib["name"]:tmp})



            return dicc
        else:
            return "Error"


    def dameSigVerison(self,carpeta):
        rut=self.xmlFileBase+carpeta
        listado =os.listdir(rut)
        tmp     =["1"]
        listR=[]
        for elem in listado:
            fx="metadata"
            ex=".xml"
            if elem.find(ex)>-1 and elem.find(fx)>-1:
                version=elem[len(fx):elem.find(ex)]
                listR.append(version)
        if len(listR)==0:
            return "1"
        if len(listR)==1:
            if len(listR[0])==0:
                return "1"

        listR.sort()
        nex=listR[-1]
        resultado = str(int(nex[1:])+1)
        return resultado

    def creatNewXmlMetadata(self,name,dato):
        nodo=ET.Element('Metadata',{'mode':'accumulate','name':name})
        nodo.text=dato
        return nodo


    def saveFileNuevoFile(self,obModificado,operarioD):
        """Genera y guarda el xml del formulario Nuevo Item"""
        listlog=[]
        xcolec=obModificado["nombreColeccion"]
        xserie=obModificado["nomSerie"]
        xsubSerie=obModificado["nomSubSerie"]





        docTypeHeader=u'<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE DirectoryMetadata SYSTEM \"http://greenstone.org/dtd/DirectoryMetadata/1.0/DirectoryMetadata.dtd \">'
        root = ET.Element("DirectoryMetadata")
        fset = ET.SubElement(root, "FileSet")
        fm=    ET.SubElement(fset, "FileName")
        fm.text=".*"
        fechaString     =time.strftime("%d/%m/%Y")+"_"+(time.strftime("%H:%M:%S"))
        desc= ET.SubElement(fset, "Description")


        for itemForm in obModificado["metadatos"]:
            itFnom =  itemForm[0]
            itFtext=  itemForm[1]



            if itFnom=="ae.itemcolaborador":



                for colab in itFtext.split("\r\n"):
                    tmpM= ET.SubElement(desc, "Metadata",mode="accumulate" ,name=itFnom)
                    tmpM.text=colab
            else:
                if itFnom=="ae.itemlenguaiso":
                    for elem in itFtext:
                        tmpM= ET.SubElement(desc, "Metadata",mode="accumulate" ,name=itFnom)
                        tmpM.text=elem
                else:
                    tmpM= ET.SubElement(desc, "Metadata",mode="accumulate" ,name=itFnom)
                    tmpM.text=itFtext






        xmlstr=minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        newfilename=obModificado["folder"]+"/metadata.xml"
        newstr=docTypeHeader+xmlstr

        userNom = self.creatNewXmlMetadata("ae.agentepersonanombre",operarioD['nombre'])
        tipoUser = self.creatNewXmlMetadata("ae.agentepersonatipo",'creador')
        fechaS = self.creatNewXmlMetadata("ae.creacionfecha",fechaString)
        copiXml.find(".//FileSet/Description").append(userNom)
        copiXml.find(".//FileSet/Description").append(tipoUser)
        copiXml.find(".//FileSet/Description").append(fechaS)

        try:
            f=open(newfilename,"wr+")
            f.write(newstr.encode('utf8'))
            os.chmod(newfilename, 0664)
            f.close()
            logstr=newfilename
            listlog.insert(0,logstr)
        except:
            e = sys.exc_info()[0]
            print "Problema: %s"% e
            logstr=newfilename
            listlog.insert(0,"error")

        return listlog


    def componeDatos(self,indice,xmldata,formdata):
        """dado una lista de metadatos, busca los valores en los datos llegados del formulario y en los datos
           del XML y los devuelve en un diccionario.
        """
        dit={}
        for ind in indice:
            valXML=u""
            valForm=u""

            valorXML=xmldata.findall('.//Metadata[@name="'+ind+'"]')

            if len(valorXML)>0:
                if len(valorXML)==1:
                    valXML=valorXML[0].text+u""
                else:
                    tmpXML=[]
                    for nodo in valorXML:
                        tmpXML.append(u"%s"%nodo.text)
                    valXML=tmpXML

            if ind in formdata.keys():
                valForm=formdata[ind]

                if isinstance(valForm,list):
                    if len(valForm)==1:
                        valForm=formdata[ind][0]
                    else:
                        valForm=formdata[ind]

                elif ind in ("ae.itemautor","ae.itemcolaborador"):
                    responsables= formdata[ind].split("\r\n")
                    if len(responsables)==1:
                        autor=responsables[0]
                        if autor!="":
                            valForm=[]
                            valForm.append(u"%s"%autor)
                    elif len(responsables)>1:
                        valForm=[]
                        for autor in responsables:
                            if autor!="":
                                valForm.append(u"%s"%autor)
            if valXML==u"" and isinstance(valForm,list):
                valXML=[u""]
            if valForm==u"" and isinstance(valXML,list):
                valForm=[u""]
            dit[ind]=(valXML,valForm)
        return dit


    def saveFile(self,obModificado,tipoDato,operarioD):
        """guarda los datos en el xml"""
        #los elementos que vienen en un array y que es necesario guardarlo con un tag metadata independiente
        multiplesValores=["ae.itemlenguaiso","ae.serielenguaiso","ae.itemcolaborador"]

        listlog=[]
        logstr=""
        pathFolder  =obModificado["idColec"]+"/"+obModificado["ruta"]
        pathFolder  =obModificado["folder"]
        version     =self.dameSigVerison(pathFolder)

        newfilename =obModificado["ruta"].replace("metadata.xml","metadataV"+version+".xml")
        newfilename =self.xmlFileBase+obModificado["idColec"]+"/"+newfilename
        rm          =self.openF(obModificado["ruta"],obModificado["idColec"])
        fechaString =time.strftime("%d/%m/%Y")+"_"+(time.strftime("%H:%M:%S"))
        hayCambios=False

        if rm == False:
             listlog.insert(0,"error")
             listlog.insert("no se pudo abrir la ruta al metadata.xml")
             return listlog

        #Nuevo Encabezado para el xml
        docTypeHeader='<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE DirectoryMetadata SYSTEM \"http://greenstone.org/dtd/DirectoryMetadata/1.0/DirectoryMetadata.dtd \">'
        #Copio el XML base
        copiXml=self.miXml.getroot()


        #compongo en un lista los valores del xml y del formulario para
        #compararlos
        if tipoDato =="serie":
            listaDatos=self.componeDatos(FinfoMetadatosSerie.values(),copiXml,obModificado["metadatos"])
        elif tipoDato =="subSerie":
            listaDatos=self.componeDatos(FinfoMetadatoSubSerie.values(),copiXml,obModificado["metadatos"])
        elif tipoDato=="item":
            listaDatos=self.componeDatos(FinfoMetaItem.values(),copiXml,obModificado["metadatos"])

        for met in listaDatos.keys():
            val1=listaDatos[met][0]
            val2=listaDatos[met][1]

            if val1!=val2:
                hayCambios=True

        if not hayCambios:
            print "no hay cambios"
            listlog.insert(0,"sin cambios")
            return listlog

        for nomMeta in listaDatos.keys():
            valorDelXML=listaDatos[nomMeta][0]
            valorDelFORM=listaDatos[nomMeta][1]
            textareaDistintos="iguales"
            itemXml=copiXml.findall('.//Metadata[@name="'+nomMeta+'"]')
            
            
            
            if nomMeta == "ae.itemalcance" or nomMeta == "ae.itemanotacion":
                #separo en lineas porque hay un error de parseo del xml para levantar
                #los /r o los /n
                ii=0
                lineasA=valorDelXML.splitlines()
                lineasB=valorDelFORM.splitlines()

                if len(lineasA)==len(lineasB):
                    for linea in lineasA:
                        if lineasA[ii] !=  lineasB[ii]:
                            textareaDistintos="modifico"
                            break;
                        ii+=1

                    if textareaDistintos == "modifico":
                        #aca modifico
                        itemXml[0].text(valorDelFORM)

                elif len(lineasA)==0 and len(lineasB)>0:
                    textareaDistintos="agrego"
                    no=self.creatNewXmlMetadata(nitemXmlomMeta,valorDelFORM)
                    copiXml.find(".//FileSet/Description").append(no)
                elif len(lineasA)>0 and len(lineasB)==0:
                    textareaDistintos="elimino"
                    copiXml.find(".//FileSet/Description").remove(itemXml[0])
            else:
                accion=""
                if valorDelXML!=valorDelFORM:
                    if isinstance(valorDelXML,list):
                        #borro todos los elementos del xml

                        for nodoX in itemXml:
                            copiXml.find(".//FileSet/Description").remove(nodoX)

                        if len(valorDelFORM)>0:
                            for valFM in valorDelFORM:
                                no=self.creatNewXmlMetadata(nomMeta,valFM)
                                copiXml.find(".//FileSet/Description").append(no)

                    elif isinstance(valorDelXML,str) or isinstance(valorDelXML,unicode):

                        if valorDelXML=="" and valorDelFORM!="":
                            #agrego
                            no=self.creatNewXmlMetadata(nomMeta,valorDelFORM)
                            copiXml.find(".//FileSet/Description").append(no)

                        if valorDelXML[0]!="" and valorDelForm[0]=="":
                            #borro
                            pass
                            
                        if valorDelXML[0]!="" and valorDelForm[0]!="":
                            #modifico
                            itemXml.text=valFM
                            pass

            #----ACtualizo DATOS
            #Si estan en el XML y el FORM y son distintos





            #----Agrego Nuevos DATOS
            #Si estan en el FORM y no estan en el XML





            #----Elimino Nuevos DATOS
            #Si estan en el XML y en el FORM está vacios






        return ""
        userNom = self.creatNewXmlMetadata("ae.agentepersonanombre",operarioD['nombre'])
        tipoUser = self.creatNewXmlMetadata("ae.agentepersonatipo",'revisor')
        fechaS = self.creatNewXmlMetadata("ae.edicionfecha",fechaString)
        copiXml.find(".//FileSet/Description").append(userNom)
        copiXml.find(".//FileSet/Description").append(tipoUser)
        copiXml.find(".//FileSet/Description").append(fechaS)

        xmlstrA=ET.tostring(copiXml)
        xmlstr=minidom.parseString(xmlstrA).toprettyxml(encoding='UTF-8')


        try:
            f=open(newfilename,"wr+")
            newstr=docTypeHeader+xmlstr
            f.write(newstr)
            f.close()
            logstr=newfilename
            listlog.insert(0,logstr)

        except:
            e = sys.exc_info()[0]
            print "Problema: %s"% e
            logstr=newfilename
            listlog.insert(0,"error")

        return listlog

        #return listlog.insert(0,"sin cambios")
        #for miMeta in FinfoMetadatosSerie.values():
        #    numCampo=FinfoMetadatosSerie.values().index(miMeta)
        #    tituloCampo=serieTitle[numCampo]

    def dameMetadata(self,strMeta):
        try:
            root = self.miXml.getroot()
        except:
            print "no se puede parsear el xml"
            return []

        metadato=""

        if len(self.miXml.findall(u'.//Metadata[@name="'+strMeta+'"]'))>0:
            meta=self.miXml.findall(u'.//Metadata[@name="'+strMeta+'"]')[0].text
            metadato=meta

        return metadato





    def getMetadataForItem(self):
        """Metodo que devuelve un diccionario de METADATOS ITEMS para json"""
        res=self.getMetadataFor(FinfoMetaItem)
        return res

    def getMetadataForSubSerie(self):
        """Metodo que devuelve un diccionario de METADATOS SUBSERIE para json"""
        res=self.getMetadataFor(FinfoMetadatoSubSerie)
        return res

    def getMetadataForSerie(self):
        """Metodo que devuelve un diccionario de METADATOS SERIE para json"""
        res=self.getMetadataFor(FinfoMetadatosSerie)

        return res

    def getMetadataFor(self,infoMetadatos):
        """METODO AUXILIAR PARA DEVOLVER METADATOS EN EL DICIONARIO infoMetadatos,infoMetadatoSubSerie,infoMetaItem de EditGS"""
        res=[]
        for ke,val in infoMetadatos.items():
            res.append({val:self.dameMetadata(val)})
        return res
