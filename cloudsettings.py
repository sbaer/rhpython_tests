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
    if data.has_key("error"): return data
    
    state = Rhino.ApplicationSettings.AppearanceSettings.GetDefaultState()
    Rhino.ApplicationSettings.AppearanceSettings.UpdateFromState(state)
    state = Rhino.ApplicationSettings.EdgeAnalysisSettings.GetDefaultState()
    Rhino.ApplicationSettings.EdgeAnalysisSettings.UpdateFromState(state)
    def restoresetting(section, name, setting):
        try:
            s = "Rhino.ApplicationSettings."+section+"." + name
            if name.endswith("Color"):
                s += "=System.Drawing.ColorTranslator.FromHtml(\"" + setting + "\")"
            else:
                if type(setting) is str: s += "='" + setting + "'"
                else: s+= "=" + str(setting)
            exec(s)
        except:
            print sys.exc_info()
    for setting, val in data.items():
        if type(val) is dict:
            section_name = setting
            for k,v in val.items(): restoresetting(section_name, k, v)
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
    if data.has_key("error"):
        if data["error"]=="not_found": data = {}
        else: return data #something unexpected happened

    data["_id"] = id
    if password: data["password_hash"] = hashlib.md5(password).hexdigest()
    
    def additem(dict, section, name, defaults):
        s = "Rhino.ApplicationSettings."+section+"." + name
        sameasdefault = eval( "defaults."+name+"=="+s )
        if not sameasdefault:
            print "  ", s
            item = eval(s)
            if type(item) is System.Drawing.Color:
                item = System.Drawing.ColorTranslator.ToHtml(item)
            dict[name] = item
    
    section = "AppearanceSettings"
    subdict = {}
    defaults = Rhino.ApplicationSettings.AppearanceSettings.GetDefaultState()
    additem(subdict, section, "CommandPromptBackgroundColor", defaults)
    additem(subdict, section, "CommandPromptHypertextColor", defaults)
    additem(subdict, section, "CommandPromptTextColor", defaults)
    additem(subdict, section, "CrosshairColor", defaults)
    additem(subdict, section, "CurrentLayerBackgroundColor", defaults)
    additem(subdict, section, "DefaultObjectColor", defaults)
    additem(subdict, section, "FeedbackColor", defaults)
    additem(subdict, section, "FrameBackgroundColor", defaults)
    additem(subdict, section, "LockedObjectColor", defaults)
    additem(subdict, section, "PageviewPaperColor", defaults)
    additem(subdict, section, "SelectedObjectColor", defaults)
    additem(subdict, section, "TrackingColor", defaults)
    additem(subdict, section, "ViewportBackgroundColor", defaults)
    additem(subdict, section, "WorldCoordIconXAxisColor", defaults)
    additem(subdict, section, "WorldCoordIconYAxisColor", defaults)
    additem(subdict, section, "WorldCoordIconZAxisColor", defaults)
    additem(subdict, section, "DefaultFontFaceName", defaults)
    additem(subdict, section, "ShowCrosshairs", defaults)
    additem(subdict, section, "ShowFullPathInTitleBar", defaults)
    if len(subdict)>0: data[section] = subdict
    
    section = "EdgeAnalysisSettings"
    subdict = {}
    defaults = Rhino.ApplicationSettings.EdgeAnalysisSettings.GetDefaultState()
    additem(subdict, section, "ShowEdgeColor", defaults)
    additem(subdict, section, "ShowEdges", defaults)
    if len(subdict)>0: data[section] = subdict

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
                print "- Saving non-default settings to cloud"
                cloudsave(name, password)
                print "- Settings have been saved under", name
