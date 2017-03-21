 # -*- coding: utf-8 -*-
__author__ = 'Paul'
import urllib2
import xml.etree.ElementTree as ET
import os
import sys
from arcas.content.config import     infoMetadatosSerie as FinfoMetadatosSerie
from arcas.content.config import     infoMetadatoSubSerie as FinfoMetadatoSubSerie
from arcas.content.config import     infoMetaItem as FinfoMetaItem


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
        #if ruta.find("web")==-1:
        #    self.xmlFileResto=ruta.split(coll)[1]
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
    
    def saveFile(self,obModificado):
        """
            guarda los datos en el xml
        """
        listlog=[]
        logstr=""
        pathFolder      =obModificado["idColec"]+"/"+obModificado["ruta"]
        pathFolder      =obModificado["folder"]
        version         =self.dameSigVerison(pathFolder)        
        #newfilename     =obModificado["ruta"].replace("metadata.xml",self.xmlFileResto+"metadataV"+version+".xml")
        newfilename     =obModificado["ruta"].replace("metadata.xml","metadataV"+version+".xml")
        newfilename     =self.xmlFileBase+obModificado["idColec"]+"/"+newfilename
        rm              =self.openF(obModificado["ruta"],obModificado["idColec"])

        if rm == False:
            return False
        
        #elemino todos los metadatos del xml cargado
        docTypeHeader='<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE DirectoryMetadata SYSTEM \"http://greenstone.org/dtd/DirectoryMetadata/1.0/DirectoryMetadata.dtd \">'
        copiXml=self.miXml.getroot()
        
        
        #actualizo los que estan
        for itemXml  in copiXml.find(".//FileSet/Description").findall(".//Metadata"):
            itXnom=itemXml.attrib["name"]
            itXtext=itemXml.text
            
            for itemForm in obModificado["metadatos"]:
                itFnom =  itemForm[0]
                itFtext=  itemForm[1]

                if itFnom==itXnom:
                    if itFtext=="":
                        #Si en el formulario el metadato está vacio lo borro el XNL                        
                        copiXml.find(".//FileSet/Description").remove(itemXml)               
                        #logstr="%s quedó vacio y se eliminó del metadata.xml" %itFnom
                        #listlog.append(logstr)
                    else:
                        #actualizo el dato en el XNL con el valor que viene del form
                        #puede venir una lista por los idiomas o un str 
                        if type(itFtext)==type([]):
                            if itXtext!=itFtext[0]:
                                itemXml.text=itFtext[0]
                                logstr="actualizado> %s: %s" %(itFnom,itFtext[0])
                                listlog.append(logstr)
                        else:
                            itemXml.text=itFtext
                            if itXtext!=itFtext:
                                itemXml.text=itFtext
                                logstr="actualizado> %s: %s" %(itFnom,itFtext)
                                listlog.append(logstr)
                        flagMatch=True
                    break
                
                
        ##agrego el elemento nuevo que no estaban en el FS XML mingshaobi     
        for itemForm in obModificado["metadatos"]:
            itFnom =  itemForm[0]
            itFtext=  itemForm[1]
            
            if type(itFtext)==type([]):
                itFtext=itFtext[0]

            flagMatch=False
            
            for itemXml  in copiXml.find(".//FileSet/Description").findall(".//Metadata"):
                itXnom=itemXml.attrib["name"]
                if itXnom == itFnom:
                    flagMatch=True
                    break

            if flagMatch==False:

                if itFtext!="":
                    no=self.creatNewXmlMetadata(itFnom,itFtext)
                    copiXml.find(".//FileSet/Description").append(no)
                    logstr="nuevo> %s: %s." %(itFnom,itFtext)
                    listlog.append(logstr)
        
        xmlstr=ET.tostring(copiXml)
        
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
