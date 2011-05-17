"""Example for working with a couchdb database
Stores/retrieves appearance setting colors in a couchdb database
hosted in a test account I set up on cloudant.com
"""
import sys, json, urllib, urllib2
import rhinoscriptsyntax as rs
import System
import Rhino

couchdb_url = "https://stevebaer.cloudant.com/rhinotest"

def cloudrestore(id):
    url = couchdb_url + "/" + id
    f = urllib.urlopen(url)
    data = json.load(f)
    f.close()
    if data.has_key("error") or not data.has_key("AppearanceSettings"):
        return data
    def restorecolor(name, color):
        try:
            s = "Rhino.ApplicationSettings.AppearanceSettings." + name
            s += "=System.Drawing.ColorTranslator.FromHtml(\"" + color + "\")"
            exec(s)
        except:
            print sys.exc_info()
    subdict = data["AppearanceSettings"]
    for k, v in subdict.items():
        restorecolor(k,v)

	
def cloudsave(id):
    def addcolor(dict, name):
        s = "Rhino.ApplicationSettings.AppearanceSettings." + name
        color = eval(s)
        dict[name] = System.Drawing.ColorTranslator.ToHtml(color)
    
    #see if this document already exists in the couchdb
    url = couchdb_url + "/" + id
    f = urllib.urlopen(url)
    data = json.load(f)
    f.close()
    if data.has_key("error"):
        if data["error"]=="not_found":
            data = {}
        else:
            #something unexpected happened
            return data

    data["_id"] = id
    subdict = {}
    if data.has_key("AppearanceSettings"):
        subdict = data["AppearanceSettings"]
    else:
        data["AppearanceSettings"] = subdict
    addcolor(subdict, "CommandPromptBackgroundColor")
    addcolor(subdict, "CommandPromptHypertextColor")
    addcolor(subdict, "CommandPromptTextColor")
    addcolor(subdict, "CrosshairColor")
    addcolor(subdict, "FeedbackColor")
    addcolor(subdict, "FrameBackgroundColor")
    addcolor(subdict, "LockedObjectColor")
    addcolor(subdict, "PageviewPaperColor")
    addcolor(subdict, "SelectedObjectColor")
    addcolor(subdict, "TrackingColor")
    addcolor(subdict, "ViewportBackgroundColor")
    addcolor(subdict, "WorldCoordIconXAxisColor")
    addcolor(subdict, "WorldCoordIconYAxisColor")
    addcolor(subdict, "WorldCoordIconZAxisColor")
    
    j = json.dumps(data)
    req = urllib2.Request(couchdb_url, j, {"content-type":"application/json"})
    stream = urllib2.urlopen(req)
    response = stream.read()
    stream.close()
    return response
    

def getinput():
    restore = rs.GetBoolean("Get or set", [("Direction", "SaveSettingsToCloud", "GetSettingsFromCloud")], True)
    if restore is None: return
    restore = restore[0]
    name = rs.GetString("Name for settings set")
    if not name: return
    return restore, name

if __name__ == "__main__":
    print "Rhino Appearance Settings"
    input = getinput()
    if input is not None:
        restore, name = input
        if restore:
            print "- Restoring settings saved in cloud"
            cloudrestore(name)
        else:
            print "- Saving settings to cloud"
            cloudsave(name)
        print "- Done"
