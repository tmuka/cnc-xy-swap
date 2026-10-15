import json, sys, zipfile

src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
files = {i.filename: zin.read(i) for i in zin.infolist()}

def xy(p):  # old (x, y) -> new (x, y):  new X = -old Y, new Y = old X
    p["x"], p["y"] = -p["y"], p["x"]

def dumps(o):
    return (json.dumps(o, indent=2) + "\n").encode()

# settings.json
s = json.loads(files["settings.json"])
assert s["homeLocation"] == "back-left"
s["homeLocation"] = "front-left"
kz = s["advanced"]["keepoutZone"]
mn, mx = kz["min"], kz["max"]
kz["min"] = {"x": -mx["y"], "y": mn["x"]}
kz["max"] = {"x": -mn["y"], "y": mx["x"]}
px, py, pz = s["parkingLocation"].split(",")
s["parkingLocation"] = f"{py.lstrip('-') if py.startswith('-') else '-' + py},{px},{pz}"
files["settings.json"] = dumps(s)

# Rapid Change ATC (enabled)
k = "plugin-config/com.ncsender.rapidchangeatc/config.json"
c = json.loads(files[k])
for m in c["magazines"]:
    assert m["orientation"] == "X"; m["orientation"] = "Y"; xy(m["slot1"])
assert c["orientation"] == "X"; c["orientation"] = "Y"
for key in ("pocket1", "toolSetter", "manualTool"):
    xy(c[key])
files[k] = dumps(c)

# Manual Tool Changer (disabled, converted anyway)
k = "plugin-config/com.ncsender.manualtoolchange/config.json"
c = json.loads(files[k])
for key in ("pocket1", "toolSetter", "parking"):
    xy(c[key])
files[k] = dumps(c)

# Macros: exact text replacements, each must match once
mac = {
 "macros/9004.macro": [("g53 g0 x883 y-811.795", "g53 g0 x811.795 y883")],
 "macros/9005.macro": [(";g53 g0 x883 y-811", ";g53 g0 x811 y883"),
                       ("g53 g0 x829 y-811 (x-54mm)", "g53 g0 x811 y829 (y-54mm)")],
 "macros/9012.macro": [("g53 g0 x718 y-811", "g53 g0 x811 y718")],
 "macros/9006.macro": [("G54 G90 G0 X1.245  Y129;", "G54 G90 G0 X-129 Y1.245;")],
 "macros/9007.macro": [("G54 G90 G0 X-1.245 Y-129;", "G54 G90 G0 X129 Y-1.245;")],
 "macros/9011.macro": [("( PROGRAM: Laser Y+38 )", "( PROGRAM: Laser X-38 )"),
                       ("G91 G0 Y38;", "G91 G0 X-38;")],
 "macros/9008.macro": [("( PROGRAM: Laser Y-38 )", "( PROGRAM: Laser X+38 )"),
                       ("G91 G0 Y-38;", "G91 G0 X38;")],
 "macros/9002.macro": [(";g53 g0 x883 y-811 //atc lowest", ";g53 g0 x811 y883 //atc lowest"),
                       ("g53 g0 x[882.7+ 45*7] y-811.785", "g53 g0 x811.785 y[882.7+ 45*7]"),
                       (";g53 g0 x1197.7 y-811", ";g53 g0 x811 y1197.7")],
 "macros/9010.macro": [("g53 g0 X118.503 Y-685.985", "g53 g0 X685.985 Y118.503")],
}
for k, reps in mac.items():
    t = files[k].decode()
    for a, b in reps:
        assert t.count(a) == 1, (k, a)
        t = t.replace(a, b)
    files[k] = t.encode()

with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
    for i in zin.infolist():
        zout.writestr(i.filename, files[i.filename])
