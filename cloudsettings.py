import json
import urllib
import urllib2
import rhinoscriptsyntax as rs
import System
import Rhino

USERNAME=None

def getsettings():
    if not USERNAME:
        USERNAME = rs.GetString("UserName:")
        if not USERNAME: return


def setsettings():
    if not USERNAME:
        USERNAME = rs.GetString("UserName:")
        if not USERNAME: return



def cloudant():
    s = "https://stevebaer.cloudant.com/rhinotest/point"
    f = urllib.urlopen(s)
    rc = json.load(f)
    f.close()
    return rc["location"]
    

def cloudadd(user):
    items = {}
    items["user"] = user
    color = Rhino.ApplicationSettings.AppearanceSettings.CommandPromptBackgroundColor
    items["CommandPromptBackgroundColor"] = System.Drawing.ColorTranslator.ToHtml(color)
    color = Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor
    items["ViewportBackgroundColor"] = System.Drawing.ColorTranslator.ToHtml(color)
    color = Rhino.ApplicationSettings.AppearanceSettings.CommandPromptTextColor
    items["CommandPromptTextColor"] = System.Drawing.ColorTranslator.ToHtml(color)
    
    j = json.dumps(items)
    req = urllib2.Request("https://stevebaer.cloudant.com/rhinotest", j, {"content-type":"application/json"})
    stream = urllib2.urlopen(req)
    response = stream.read()
    stream.close()
    print response
    
    
cloudadd("steve")