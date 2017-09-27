#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Paul'
import urllib2
import xml.etree.ElementTree as ET
import os
import sys
import time
import string
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


            if isinstance(itFtext,list):                               
                for dato in itFtext:
                    tmpM= ET.SubElement(desc, "Metadata",mode="accumulate" ,name=itFnom)
                    tmpM.text=dato
            else:                
                tmpM= ET.SubElement(desc, "Metadata",mode="accumulate" ,name=itFnom)
                tmpM.text=itFtext


        tmpM= ET.SubElement(desc, "Metadata",mode="accumulate" ,name="ae.agentepersonanombre")
        tmpM.text=operarioD['nombre']
        
        tmpM= ET.SubElement(desc, "Metadata",mode="accumulate" ,name="ae.agentepersonatipo")
        tmpM.text=u"creador"
        
        tmpM= ET.SubElement(desc, "Metadata",mode="accumulate" ,name="ae.creacionfecha")
        tmpM.text=fechaString

        xmlstr=minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")[22:]
        newfilename=obModificado["folder"]+"/metadata.xml"
        newstr=docTypeHeader+xmlstr

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
                                

            if isinstance(valForm,list) and not isinstance(valXML,list):
                tmp=[valXML,]
                valXML=tmp
            if isinstance(valXML,list) and not isinstance(valForm,list):
                tmp=[valForm,]
                valForm=tmp
           
                
            dit[ind]=(valXML,valForm)
        return dit


    def saveFile(self,obModificado,tipoDato,operarioD):
        """guarda los datos en el xml:
        
        los elementos que vienen en un array y que es necesario guardarlo con un tag metadata independiente
        devuelve una lista que en la 
        posicion 0 tiene el estatus 
        y en la posicion 1 el mensaje...
        despues el registro de los cambios.
        
        """
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
        elif tipoDato=="subSerie":
            listaDatos=self.componeDatos(FinfoMetadatoSubSerie.values(),copiXml,obModificado["metadatos"])
        elif tipoDato=="item":
            listaDatos=self.componeDatos(FinfoMetaItem.values(),copiXml,obModificado["metadatos"])

        for met in listaDatos.keys():
            val1=listaDatos[met][0]
            val2=listaDatos[met][1]
            
            
            if "ae.itemalcance" == met or  "ae.itemanotacion" == met: 
                if not isinstance(val1,list) and not isinstance(val2,list):
                    val1 = string.replace(val1, '\r\n', '\n')
                    val1 = string.replace(val1, '\r', '\n')                
                    val2 = string.replace(val2, '\r\n', '\n')
                    val2 = string.replace(val2, '\r', '\n')                

            if val1!=val2:
                hayCambios=True

        if not hayCambios:            
            listlog.insert(0,"sin cambios")
            listlog.append("No se guradaron cambios")
            return listlog



        for nomMeta in listaDatos.keys():
            valorDelXML=listaDatos[nomMeta][0]
            valorDelFORM=listaDatos[nomMeta][1]
            textareaDistintos="iguales"
            itemXml=copiXml.findall('.//Metadata[@name="'+nomMeta+'"]')
            
            #borro todos los nodos
            for nodoX in itemXml:
                copiXml.find(".//FileSet/Description").remove(nodoX)      

            if isinstance(valorDelFORM,list):                
                
                if len(valorDelFORM)>0:
                        if len(valorDelXML)>0:
                            if len(valorDelXML[0])>0:         
                                if valorDelFORM!=valorDelXML:                            
                                    logstr="%s, actualizado: %s" %(nomMeta,valorDelFORM)
                                    listlog.append(logstr)
                            
                            else:
                                logstr="%s, nuevo metadato: %s" %(nomMeta,valorDelFORM)
                                listlog.append(logstr)

                        #agrego los nuevos nodos
                        for valFM in valorDelFORM:
                            no=self.creatNewXmlMetadata(nomMeta,valFM)
                            copiXml.find(".//FileSet/Description").append(no)

                else:
                    if len(valorDelXML)>0:
                        logstr="%s, metadato eliminado" %(nomMeta)
                        listlog.append(logstr)
                        
                        

            else:
                if len(valorDelFORM.strip())>0:
                    #agrego los nuevos nodos

                    if bool(valorDelXML.strip()):
                        if (valorDelXML!=valorDelFORM):
                            cm=True
                            if "ae.itemalcance" == nomMeta or  "ae.itemanotacion" == nomMeta: 
                                val1=valorDelFORM
                                val2=valorDelXML
                                
                                val1 = string.replace(val1, '\r\n', '\n')
                                val1 = string.replace(val1, '\r', '\n')                
                                val2 = string.replace(val2, '\r\n', '\n')
                                val2 = string.replace(val2, '\r', '\n')
                                
                                if val1 == val2:
                                    cm=False

                            if cm:                       
                                logstr="%s, actualizado: %s" %(nomMeta,valorDelFORM)
                                listlog.append(logstr)
                    else:                        
                        logstr=" %s, nuevo metadato: %s" %(nomMeta,valorDelFORM)
                        listlog.append(logstr)
                    
                    
                        
                    no=self.creatNewXmlMetadata(nomMeta,valorDelFORM)
                    copiXml.find(".//FileSet/Description").append(no)
                else:
                    if len(valorDelXML.strip())>0:
                        logstr="%s, metadato eliminado" %(nomMeta)
                        listlog.append(logstr)
                    
        
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
            lstr=u"cambios guardados en "+newfilename
            listlog.insert(0,"ok")
            listlog.insert(1,lstr)
        except IOError:
            e = sys.exc_info()[0]
            listlog.insert(0,"error")
            listlog.insert(1,e.__doc__)
        except:
            print('An error occured.')
            e = sys.exc_info()[0]
            #logstr=newfilename
            listlog.insert(0,"error")
            listlog.insert(1,e)

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
