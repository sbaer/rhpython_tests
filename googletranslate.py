"""Google translate functions for translating text"""
import rhinoscriptsyntax as rs
import json, urllib
import scriptcontext

# Api key that I (Steve Baer) got from Google
# http://code.google.com/apis/console-help/#UsingKeys
# You might want to generate your own key, but I don't care
# if you continue to use this one.
KEY = "AIzaSyAZGoS-GjZGaSHZMZdoczfdUtWTjm_D-p4"

def translate(text, source="en", target="fr"):
    """Translate text from one language to another. Returns the
    translated text on success or None on failure
    """
    # see if we already have a cached answer
    cache_dict_name = "translate " + source + ":" + target
    if scriptcontext.sticky.has_key(cache_dict_name):
        cache = scriptcontext.sticky[cache_dict_name]
        if cache.has_key(text): return cache[text]
    
    url = "https://www.googleapis.com/language/translate/v2"
    url += "?key=" + KEY
    url += "&q="+urllib.quote(text.encode('utf-8'))
    url += "&source="+source
    url += "&target="+target
    f = urllib.urlopen(url)
    s = f.read()
    f.close()
    s = unicode(s, 'utf-8')
    rc = json.loads(s)
    if rc.has_key("data"):
        translated = rc["data"]["translations"][0]["translatedText"]
        if not scriptcontext.sticky.has_key(cache_dict_name):
            scriptcontext.sticky[cache_dict_name] = {}
        scriptcontext.sticky[cache_dict_name][text] = translated
        return translated

# use __name__ test to determine if this script is directly being
# executed or if it is being loaded as a librar
if( __name__=="__main__" ):
    if rs.ContextIsGrasshopper():
        spanish = translate(english, "en", "es")
        german = translate(english, "en", "de")
        french = translate(english, "en", "fr")
        italian = translate(english, "en", "it")
        japanese = translate(english, "en", "ja")
    elif rs.ContextIsRhino():
        # get text dots and translate their contents
        dots = rs.GetObjects("Select dots to translate", rs.filter.textdot)
        if dots:
            langs = { "English":"en",
                      "ChineseSimplified":"zh-CN",
                      "ChineseTraditional":"zh-TW",
                      "Czech":"cs",
                      "French":"fr",
                      "German":"de",
                      "Italian":"it",
                      "Japanese":"ja",
                      "Korean":"ko",
                      "Polish":"pl",
                      "Spanish":"es"
                     }
            source_lang = rs.GetString("source", "English", langs.keys())
            source_lang = langs[source_lang]
            target_lang = rs.GetString("target", "Spanish", langs.keys())
            target_lang = langs[target_lang]
            for dot in dots:
                s = rs.TextDotText(dot)
                s = translate(s, source_lang, target_lang)
                rs.TextDotText(dot, s)
