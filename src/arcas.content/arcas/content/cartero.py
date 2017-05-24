# -*- coding: utf-8 -*-
__author__ = 'Paul'

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.CMFCore.utils import getToolByName
from arcas.content.config import MAIL_ADMIN , MAIL_COORDINADOR

class Cartero(object):
    """Manda Mails de las modificaciones en los formilarios de greenstone"""    
    
    def encabezado(self):
        sender=MAIL_ADMIN
        mt=getToolByName(self.context,"portal_membership")        
        nombreColeccion=dicDatos["nombreColeccion"]
        operarioMail    = mt.getAuthenticatedMember().getProperty('email',None)
        operarioNombre  = mt.getAuthenticatedMember().getProperty('fullname',None)      
        if operarioMail=='':
            operarioMail="pablomusa@gmail.com"

        if operarioNombre=='':
            operarioNombre="Pablo Musa"

        coordinadorMail = MAIL_COORDINADOR
        reciver=[operarioMail,coordinadorMail]
        
         # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "[ARCAS] Cambios en los metadatos de un registro"
        msg['From'] = sender
        msg['To'] = reciver[0]+','+reciver[1]        
        return msg
    
    def sendModificacion(self,dicDatos):
        """Manda el mail de MODIFICACION DE UN REGISTRO"""
        rutasItem =  dicDatos["ritem"]
        rutasSerie =  dicDatos["rserie"]
        rutasSubSerie =  dicDatos["rsubserie"]
        
        msg=self.encabezado()        
        # Cuerpo del mensaje solo texto
        text = "Hola!\nSe modificaron metadatos en el Greenston de ARCAS.\n Los Archivos son: %s\n %s \n%s" %(rutasSerie,rutasSubSerie,rutasItem)       
        
        # Cuerpo del mensaje solo texto
        hhtml = u"<html><head></head><body><h3>Modificación en la coleccion: %s </h3>"%nombreColeccion
        hhtml += u"El usuario: %s, realizó modificaciones en los matadatos de ARCAS.</br>" %operarioNombre.decode("utf8")
        hhtml += u"<p>Esto es un registro básico de lo realizado:</p>"
        hhtml += u"<ul><li><b>Serie:</b><li>"
        for stra in rutasSerie:
            hhtml += '<li>%s</li>'%stra
        
        if len(rutasSerie)==1:
            hhtml += '<li>Sin cambios</li>'
            
        hhtml += u"</ul></li><li><b>SubSerie:</b><ul>"
        
        for stra in rutasSubSerie:  
            hhtml += '<li>%s</li>'%stra
        if len(rutasSubSerie)==1:
            hhtml += '<li>Sin cambios</li>'           
        hhtml += u"</ul></li><li><b>Item:</b><ul>"        
        for stra in rutasItem:            
            hhtml += '<li>%s</li>'%stra
        if len(rutasItem)==1:
            hhtml += u'<li>Sin cambios</li>'                        
        hhtml += u"</ul></li></ul>"
        hhtml += u"<hr/><p>Este es un mail automático, por favor no responder. En caso de errores "
        hhtml += u"comunicarse con mariana@fahce.unlp.edu.ar</p>Gracias.</p>"
        hhtml += u"</br></br><p></p>"
        hhtml += u"</body></html>"

        #Record the MIME types of both parts - text/plain and text/html.
 
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(hhtml.encode('utf8'), 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            s = smtplib.SMTP('localhost')
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            
            #s.sendmail(msg['From'], msg['To'], msg.as_string())
            
            s.quit()
            return True
        except Exception:
            print "Error: unable to send email"
            return False
        
        
        
        
        
        
    def sendAlta(self, datos):
        """Manda el mail de un NUEVA OBRA"""       
        
        msg=self.encabezado()
        # Cuerpo del mensaje solo texto
        text = "Se agregó un nuevo Item en la Serie: %s" %datos["serie"]
        
        # Cuerpo del mensaje solo texto
        hhtml = u"<html><head></head><body><h3>Alta de una obra en la coleccion: %s </h3>"%nombreColeccion
        hhtml += u"El usuario: %s, realizó la incorporación.</br>" %operarioNombre.decode("utf8")
        hhtml += u"<p>El documento y su adjunto se encuentrane en</p>"
        hhtml += u"</br></br><p></p>"
        hhtml += u"</body></html>"

        #Record the MIME types of both parts - text/plain and text/html.
 
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(hhtml.encode('utf8'), 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            s = smtplib.SMTP('localhost')
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            
            
            #s.sendmail(msg['From'], msg['To'], msg.as_string())
            
            s.quit()
            return True
        except Exception:
            print "Error: unable to send email"
            return False
    
    
    