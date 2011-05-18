"""Example for working with a couchdb database
Stores/retrieves appearance setting colors in a couchdb database
hosted in a test account I set up on cloudant.com
"""
import sys, json, urllib, urllib2, hashlib
import rhinoscriptsyntax as rs
import System, Rhino

couchdb_url = "https://stevebaer.cloudant.com/rhinotest"

def cloudrestore(id):
    """Retrieve settings document from a couchdb database and
    update the current application settings by these values
    Parameters:
        id: name of the document store in the database
    """
    f = urllib.urlopen(couchdb_url + "/" + id)
    data = json.load(f)
    f.close()
    if data.has_key("error") or not data.has_key("AppearanceSettings"):
        return data
    def restoresetting(name, setting):
        try:
            s = "Rhino.ApplicationSettings.AppearanceSettings." + name
            if name.endswith("Color"):
                s += "=System.Drawing.ColorTranslator.FromHtml(\"" + setting + "\")"
            else:
                if type(setting) is str: s += "='" + setting + "'"
                else: s+= "=" + str(setting)
            exec(s)
        except:
            print sys.exc_info()
    for k, v in data["AppearanceSettings"].items():
        restoresetting(k,v)
    rs.Redraw()

	
def cloudsave(id, password=None):
    """Save application settings to a document stored in a couchdb
    database.
    parameters:
        id: Name of document to save in database. A the id is always
            converted to lower case.
        password: password used to save/update settings. password is
            optional, but if you don't set one then anyone can overwrite
            these settings
    """
    #see if this document already exists in the couchdb
    id = id.lower()
    url = couchdb_url + "/" + id
    f = urllib.urlopen(url)
    data = json.load(f)
    f.close()
    hashed_password = None
    if password:
        hashed_password = hashlib.md5(password).hexdigest()
    if data.has_key("error"):
        if data["error"]=="not_found":
            data = {}
        else:
            #something unexpected happened
            return data
    elif data.has_key("password_hash") and hashed_password:
        #make sure the password matches
        if data["password_hash"]!=hashed_password:
            print "password does not match"
            return

    data["_id"] = id
    if hashed_password:
        data["password_hash"] = hashed_password
    subdict = {}
    data["AppearanceSettings"] = subdict

    def addcolor(dict, name):
        s = "Rhino.ApplicationSettings.AppearanceSettings." + name
        color = eval(s)
        dict[name] = System.Drawing.ColorTranslator.ToHtml(color)
    addcolor(subdict, "CommandPromptBackgroundColor")
    addcolor(subdict, "CommandPromptHypertextColor")
    addcolor(subdict, "CommandPromptTextColor")
    addcolor(subdict, "CrosshairColor")
    addcolor(subdict, "CurrentLayerBackgroundColor")
    addcolor(subdict, "DefaultObjectColor")
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
    subdict["DefaultFontFaceName"] = Rhino.ApplicationSettings.AppearanceSettings.DefaultFontFaceName
    subdict["ShowCrosshairs"] = Rhino.ApplicationSettings.AppearanceSettings.ShowCrosshairs
    subdict["ShowFullPathInTitleBar"] = Rhino.ApplicationSettings.AppearanceSettings.ShowFullPathInTitleBar
    
    j = json.dumps(data)
    req = urllib2.Request(couchdb_url, j, {"content-type":"application/json"})
    stream = urllib2.urlopen(req)
    response = stream.read()
    stream.close()
    return response


def getinput():
    gs = Rhino.Input.Custom.GetString()
    gs.SetCommandPrompt("Name for settings")
    direction = Rhino.Input.Custom.OptionToggle(True, "SaveSettingsToCloud", "GetSettingsFromCloud")
    gs.AddOptionToggle("direction", direction)
    while( True ):
        if gs.Get()==Rhino.Input.GetResult.Option: continue
        break
    if gs.CommandResult()!=Rhino.Commands.Result.Success:
        return
    restore = direction.CurrentValue
    name = gs.StringResult()
    return restore, name

if __name__ == "__main__":
    print "Rhino Appearance Settings"
    input = getinput()
    if input is not None:
        restore, name = input
        if restore:
            print "- Restoring settings saved in cloud"
            cloudrestore(name)
            print "- Settings restored"
        else:
            password = rs.GetString("password")
            if password:
                print "- Saving settings to cloud"
                cloudsave(name, password)
                print "- Settings have been saved under", name
