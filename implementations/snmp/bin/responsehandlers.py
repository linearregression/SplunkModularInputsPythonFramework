#add your custom response handler class to this module
import json,csv
from pysnmp.entity.rfc3413 import mibvar

#the default handler , does nothing , just passes the raw output directly to STDOUT
class DefaultResponseHandler:
    
    def __init__(self,**args):
        pass
        
    def __call__(self, response_object,destination,table=False,from_trap=False,trap_metadata=trap_metadata,split_bulk_output=False,mibView=None):        
        splunkevent =""
        
        if from_trap:
            for oid, val in response_object:
                try:
                    (symName, modName), indices = mibvar.oidToMibName(mibView, oid)                 
                    splunkevent +='%s::%s.%s =  ' % (modName, symName,'.'.join([ v.prettyPrint() for v in indices]))      
                except: # catch *all* exceptions
                    e = sys.exc_info()[1]
                    logging.error("Exception resolving OID to MIB Name: %s" % str(e))
                    splunkevent +='%s =  ' % (oid)
                try:
                    decodedVal = mibvar.cloneFromMibValue(mibView,modName,symName,val)
                    splunkevent +='%s ' % (decodedVal.prettyPrint())      
                except: # catch *all* exceptions
                    e = sys.exc_info()[1]
                    logging.error("Exception resolving OID value: %s" % str(e))
                    splunkevent +='%s ' % (val.prettyPrint()) 
            splunkevent = trap_metadata + splunkevent       
            print_xml_single_instance_mode(destination, splunkevent)
          
        elif table:
            for varBindTableRow in response_object:
                for name, val in varBindTableRow:
                    output_element = '%s = "%s" ' % (name.prettyPrint(), val.prettyPrint())                               
                    if split_bulk_output:
                        print_xml_single_instance_mode(destination, output_element)
  
                    else:    
                        splunkevent += output_element 
        else:  
            for name, val in response_object:
                splunkevent += '%s = "%s" ' % (name.prettyPrint(), val.prettyPrint())
                   
                   
        if not split_bulk_output:
            print_xml_single_instance_mode(destination, splunkevent)



# prints XML stream
def print_xml_single_instance_mode(server, event):
    
    print "<stream><event><data>%s</data><host>%s</host></event></stream>" % (
        encodeXMLText(event), server)
    
# prints XML stream
def print_xml_multi_instance_mode(server, event, stanza):
    
    print "<stream><event stanza=""%s""><data>%s</data><host>%s</host></event></stream>" % (
        stanza, encodeXMLText(event), server)
    
# prints simple stream
def print_simple(s):
    print "%s\n" % s
                             
#HELPER FUNCTIONS
    
# prints XML stream
def print_xml_stream(s):
    print "<stream><event unbroken=\"1\"><data>%s</data><done/></event></stream>" % encodeXMLText(s)

def encodeXMLText(text):
    text = text.replace("&", "&amp;")
    text = text.replace("\"", "&quot;")
    text = text.replace("'", "&apos;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("\n", "")
    return text