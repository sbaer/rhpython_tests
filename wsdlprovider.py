'''
Generate a proxy class for a SOAP web service from its WSDL.
Based on C# implementation from the DynamicWebService IronPython example.
'''

# Original script from "IronPython in Action" Book code found at
#  http://code.google.com/p/ironpython/
#  http://www.voidspace.org.uk/ironpython/
# 2 June 2011 - S. Baer
# Modified to cache the generated assemblies for performance purposes

import clr
clr.AddReference("System.Web.Services")
clr.AddReference("System.Xml")


from System.Web.Services.Description import (
    ServiceDescription, ServiceDescriptionImporter
)
from System.Web.Services.Protocols import SoapHttpClientProtocol
from System.IO import MemoryStream
from System.Net import WebClient

from System.CodeDom import (
    CodeCompileUnit, CodeNamespace
)
from System.CodeDom.Compiler import CodeDomProvider, CompilerParameters
from System.Xml.Serialization import CodeGenerationOptions



def GetBytes(url):
    'download the file at url'
    return WebClient().DownloadData(url)


def CreateWebServiceFromWsdl(wsdl):
    'convert the WSDL into an assembly containing the web service proxy classes'
    # generate codeDom from wsdl
    sd = ServiceDescription.Read(MemoryStream(wsdl))
    importer = ServiceDescriptionImporter()
    importer.ServiceDescriptions.Add(sd)

    codeCompileUnit = CodeCompileUnit()
    codeNamespace = CodeNamespace("")
    codeCompileUnit.Namespaces.Add(codeNamespace)
    importer.CodeGenerationOptions = (CodeGenerationOptions.GenerateNewAsync
        | CodeGenerationOptions.GenerateOldAsync)
    importer.Import(codeNamespace, codeCompileUnit)

    # compile CodeDom into an assembly
    provider = CodeDomProvider.CreateProvider("CS")
    compilerParams = CompilerParameters()
    compilerParams.GenerateInMemory = True
    compilerParams.IncludeDebugInformation = False
    results = provider.CompileAssemblyFromDom(compilerParams, codeCompileUnit)
    generatedAssembly = results.CompiledAssembly

    return generatedAssembly

# dictionary used to cache assemblies generated from wsdl
__assembly_cache = {}

def GetWebservice(url):
    key = url.lower()
    if not __assembly_cache.has_key(key):
        'download the WSDL for the service URL and generate an assembly from it'
        if url.lower().endswith(".asmx"): url += "?WSDL"

        data = GetBytes(url)
        assembly = CreateWebServiceFromWsdl(data)
        if not assembly: return None
        __assembly_cache[key] = assembly
    return __assembly_cache[key]


def FindProxyType(assembly):
    """if you aren't sure of the name of the proxy type that will be generated,
    use this to find it"""
    for name in dir(assembly):
        attr = getattr(assembly, name)
        if type(attr) is type and issubclass(attr, SoapHttpClientProtocol):
            return attr

