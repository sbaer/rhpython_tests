import wsdlprovider

wsdl_url = "http://api.shapeways.com/v1/wsdl.php"
username = "username"
password = "password"
application_id = "rhinotest"

assembly = wsdlprovider.GetWebservice(wsdl_url)
shapeways = assembly.SWwsdlService()
session_id = shapeways.login(username, password, application_id)
if session_id:
    printers = shapeways.getPrinters(session_id, "", application_id)
    if printers:
        for printer in printers:
            print "printer:", printer.title
            for material in printer.materials:
                print " - material ", material.title
