#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Paul'
import urllib2
import xml.etree.ElementTree as ET
import os
import sys
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
    metadatoTipoPersona="ae.agentepersonatipo"
    metadatoTipoPersonaValor=["creador","revisor"]
    metadatoTipoNombre="ae.agentepersonanombre"
    metadatoCrea="ae.datecreacion"
    
    def openF(self,ruta,coll):
        """ruta: es ruta al archivo greenston, desde el import,
        coll: es id de coleccion"""
        ruta=self.xmlFileBase+coll+"/"+ruta
        result=self.openFile(ruta)
        
        return result
                
    def openFile(self, ruta):
        print ruta
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
        if miFile:
            metas=self.miXml.find("./FileSet/Description").findall(".//Metadata")
            for elem in metas:
                dicc.update({elem.attrib["name"]:elem.text})
                
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
    
    
    def saveFileNuevoFile(self,obModificado):
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

        
        try:         
            
            f=open(newfilename,"wr+")            
            f.write(newstr.encode('utf8'))
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
            valorXML=xmldata.findall('.//Metadata[@name="'+ind+']')
            if (valorXML)>0:                
                valXML=valorXML
            else:
                valXML=""
                
            if ind in formdata.keys():
                valForm=formdata[ind]
            else:
                valForm=""
            dit[ind]=(valXML,valForm)
            
        return dit
        
        
    def saveFile(self,obModificado,tipoDato):
        """
            guarda los datos en el xml
        """
        #los elementos que vienen en un array y que es necesario guardarlo con un tag metadata independiente
        multiplesValores=["ae.itemlenguaiso","ae.serielenguaiso","ae.itemcolaborador"]
        
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
        
        #Nuevo Encabezado para el xml
        docTypeHeader='<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE DirectoryMetadata SYSTEM \"http://greenstone.org/dtd/DirectoryMetadata/1.0/DirectoryMetadata.dtd \">'
        #Copio el XML base
        copiXml=self.miXml.getroot()
        
        
        #recorro buscando cambios
       
        if tipoDato =="serie":
            listaDatos=componeDatos(FinfoMetadatosSerie.values(),copiXml,obModificado["metadatos"])           
        elif tipoDato =="subSerie":
            listaDatos=componeDatos(FinfoMetadatoSubSerie.values(),copiXml,obModificado["metadatos"])
            
        elif tipoDato=="item":
            listaDatos=componeDatos(FinfoMetaItem.values(),copiXml,obModificado["metadatos"])

            
        import pdb
        pdb.set_trace()
        
        return
        for miMeta in FinfoMetadatosSerie.values():
            numCampo=FinfoMetadatosSerie.values().index(miMeta)
            tituloCampo=serieTitle[numCampo]
        
        
        
        
        
        
        
        
        #elemeino del XML los elementos multivalor, porque los agrego al final
        #for nomMet in multiplesValores:            
        #    for itemXml  in copiXml.find('.//FileSet/Description').findall('.//Metadata[@name="'+nomMet +'"]'):                
        #        copiXml.find(".//FileSet/Description").remove(itemXml)
                
        #actualizo los que estan    
        for itemXml  in copiXml.find(".//FileSet/Description").findall(".//Metadata"):
            itXnom =itemXml.attrib["name"]
            itXtext=itemXml.text
                        
            if itXnom not in multiplesValores:                         
                for itemForm in obModificado["metadatos"].keys():
                    itFnom =  itemForm
                    itFtext=  obModificado["metadatos"][itemForm]

                    if tipoDato =="serie":
                        numCampo=FinfoMetadatosSerie.values().index(itFnom)
                        tituloCampo=serieTitle[numCampo]
                        
                    elif tipoDato =="subSerie":
                        numCampo=FinfoMetadatoSubSerie.values().index(itFnom)
                        tituloCampo=subSerieTitles[numCampo]

                    elif tipoDato=="item":
                        numCampo=FinfoMetaItem.values().index(itFnom)
                        tituloCampo=itemTitles[numCampo]

                    if itFnom==itXnom:
                        if itFtext=="":
                            #Si en el formulario el metadato está vacio lo borro el XNL                        
                            copiXml.find(".//FileSet/Description").remove(itemXml)
                            #logstr="%s quedó vacio y se eliminó del metadata.xml" %itFnom
                            #listlog.append(logstr)
                        else:
                            #actualizo el dato en el XML con el valor que viene del form
                            #puede venir una lista por los idiomas o un str 
                            if type(itFtext)==type([]):
                                if itXtext!=itFtext[0]:
                                    itemXml.text=itFtext[0]
                                    logstr="actualizado> %s[%s]: %s" %(itFnom,tituloCampo,itFtext[0])
                                    listlog.append(logstr)
                            else:
                                itemXml.text=itFtext
                                if itXtext!=itFtext:
                                    itemXml.text=itFtext
                                    try:
                                        logstr="nuevo> %s[%s]: %s." %(itFnom,tituloCampo,itFtext)
                                    except:
                                        print u'error de codificación ... lo paso a utf8'
                                        logstr="nuevo> %s[%s]: %s." %(itFnom,tituloCampo,itFtext.decode('utf8'))
                                    
                                    listlog.append(logstr)
                            flagMatch=True
                        break

        ##agrego el elemento nuevo que no estaban en el FS XML mingshaobi     
        for itemForm in obModificado["metadatos"].keys():
            itFnom =  itemForm
            itFtext=  obModificado["metadatos"][itemForm]
            
            if itFnom in multiplesValores:
                if isinstance(itFtext,unicode):
                    no=self.creatNewXmlMetadata(itFnom,itFtext)       
                    copiXml.find(".//FileSet/Description").append(no)
                elif isinstance(itFtext,list):
                    for elem in itFtext:
                        no=self.creatNewXmlMetadata(itFnom,elem)
                        copiXml.find(".//FileSet/Description").append(no)
            else:
                flagMatch=False

                if tipoDato=="serie":
                    numCampo=FinfoMetadatosSerie.values().index(itFnom)
                    tituloCampo=serieTitle[numCampo]
                elif tipoDato=="subSerie":
                    numCampo=FinfoMetadatoSubSerie.values().index(itFnom)
                    tituloCampo=subSerieTitles[numCampo]
                elif tipoDato=="item":
                    numCampo=FinfoMetaItem.values().index(itFnom)
                    tituloCampo=itemTitles[numCampo]

                for itemXml  in copiXml.find(".//FileSet/Description").findall(".//Metadata"):
                    itXnom=itemXml.attrib["name"]
                    if itXnom == itFnom:
                        flagMatch=True
                        break
                if flagMatch==False:                                
                    if itFtext!="":
                        no=self.creatNewXmlMetadata(itFnom,itFtext)
                        copiXml.find(".//FileSet/Description").append(no)
                        try:
                            logstr="nuevo> %s[%s]: %s." %(itFnom,tituloCampo,itFtext)
                        except:
                            print u'error de codificación ... lo paso a utf8'
                            logstr="nuevo> %s[%s]: %s." %(itFnom,tituloCampo,itFtext.decode('utf8'))
                        listlog.append(logstr)
        
         
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
