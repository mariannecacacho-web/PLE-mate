import os,json,sqlite3,hashlib
from flask import Flask,request,jsonify,send_from_directory
from openai import OpenAI

APP_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.environ.get("PLE_MATE_DB",os.path.join(APP_DIR,"ple_mate.db"))
MODEL=os.environ.get("OPENAI_MODEL","gpt-5.6")
app=Flask(__name__,static_folder=".",static_url_path="")
client=OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM="""You are PLE-mate: a PLE study companion AND a controlled dashboard customization assistant.

You can answer study questions and safely modify the dashboard through ONLY these structured actions:
- ADD_SUBJECT: {"type":"ADD_SUBJECT","name":"Pathology","hours":20,"hoursStudied":0,"priority":false}
- SET_HOURS: {"type":"SET_HOURS","name":"Pathology","hours":20}
- LOG_STUDY_TIME: {"type":"LOG_STUDY_TIME","name":"Pathology","hours":2}
- COMPLETE_SUBJECT: {"type":"COMPLETE_SUBJECT","name":"Pathology"}
- SET_PRIORITY: {"type":"SET_PRIORITY","name":"Pathology","priority":true}
- ADD_PIN: {"type":"ADD_PIN","text":"..."}
- SET_TRACKER_OPTION: {"type":"SET_TRACKER_OPTION","option":"showHours","value":true}
- SET_LAYOUT: {"type":"SET_LAYOUT","layout":"default|compact|focus"}
- SORT_SUBJECTS: {"type":"SORT_SUBJECTS","mode":"weakest_first"}
- SET_WIDGET: {"type":"SET_WIDGET","widget":"weekly|pinboard|subjects|countdown|settings","visible":true|false}
- CREATE_WEEKLY_GRAPH: {"type":"CREATE_WEEKLY_GRAPH"}

Interpret natural language into these actions.
Examples:
"make the tracker look compact" -> SET_LAYOUT compact.
"make the tracker look cleaner/minimal" -> SET_LAYOUT compact.
"focus me on studying" -> SET_LAYOUT focus.
"put my weakest subjects at the top" -> SORT_SUBJECTS weakest_first.
"add a weekly study-hours graph" -> CREATE_WEEKLY_GRAPH.
"remove the pinboard" -> SET_WIDGET pinboard false.
"bring back the pinboard" -> SET_WIDGET pinboard true.
"hide the countdown" -> SET_WIDGET countdown false.
"show hours remaining for every subject" -> SET_TRACKER_OPTION showHours true.
"I have 12 hours left in Surgery" -> SET_HOURS Surgery 12.
"I studied Medicine for 3 hours" -> LOG_STUDY_TIME Medicine 3.
"make Pathology a priority" -> SET_PRIORITY Pathology true.

For vague visual requests like "make the tracker look like this", infer a reasonable supported layout if the user gives a style description. If they reference an image that is not available to you, do not pretend you saw it; ask them to upload it.

Never invent study hours or progress. Never claim an unsupported feature was implemented.
Do not write arbitrary HTML/JS or modify code. Use only the actions above.

After your answer append:
ACTIONS_JSON: [...]
If no action: ACTIONS_JSON: []
Optionally append:
SUGGESTION: ...
The frontend removes these machine-readable lines before displaying the answer.
"""
def db():
    c=sqlite3.connect(DB_PATH);c.row_factory=sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,session_id TEXT,role TEXT,content TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY AUTOINCREMENT,session_id TEXT,memory TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    c.commit();return c
def sid(): return request.headers.get("X-PLE-Session","anonymous")[:120]
def history(c,s,n=40):
    rows=c.execute("SELECT role,content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",(s,n)).fetchall()
    return [{"role":r["role"],"content":r["content"]} for r in reversed(rows)]
def memories(c,s,n=30):
    rows=c.execute("SELECT memory FROM memories WHERE session_id=? ORDER BY id DESC LIMIT ?",(s,n)).fetchall()
    return [r["memory"] for r in rows]
def parse(text):
    actions=[];suggestion=None;reply=text
    if "ACTIONS_JSON:" in reply:
        reply,tail=reply.split("ACTIONS_JSON:",1)
        if "SUGGESTION:" in tail:
            raw,suggestion=tail.split("SUGGESTION:",1);suggestion=suggestion.strip()
        else: raw=tail
        try:
            actions=json.loads(raw.strip())
            if not isinstance(actions,list):actions=[]
        except: actions=[]
    if "SUGGESTION:" in reply:
        reply,suggestion=reply.split("SUGGESTION:",1);suggestion=suggestion.strip()
    return reply.strip(),actions,suggestion
@app.get("/")
def home():return send_from_directory(".", "index.html")
@app.get("/api/health")
def health():return jsonify(ok=True,model=MODEL)
@app.post("/api/chat")
def chat():
    data=request.get_json(silent=True) or {}
    msg=str(data.get("message","")).strip();dash=data.get("dashboard") or {};s=sid()
    if not msg:return jsonify(error="Message is required"),400
    if not os.environ.get("OPENAI_API_KEY"):return jsonify(error="OPENAI_API_KEY is not configured"),500
    c=db()
    c.execute("INSERT INTO messages(session_id,role,content) VALUES(?,?,?)",(s,"user",msg));c.commit()
    ctx=f"""CURRENT DASHBOARD:
Subjects: {json.dumps(dash.get("subjects",[]))}
Pins: {json.dumps(dash.get("pins",[]))}
Target: {dash.get("target","")}
Config: {json.dumps(dash.get("config",{}))}
Saved memory: {json.dumps(memories(c,s))}
"""
    r=client.responses.create(model=MODEL,input=[{"role":"developer","content":SYSTEM+"\n"+ctx},*history(c,s)],safety_identifier=hashlib.sha256(s.encode()).hexdigest()[:32])
    reply,actions,suggestion=parse(r.output_text or "")
    c.execute("INSERT INTO messages(session_id,role,content) VALUES(?,?,?)",(s,"assistant",reply))
    low=msg.lower()
    if any(x in low for x in ("my goal","i want","i'm weak","im weak","i finished","i completed","i struggle","i prefer","i studied","i'm behind","im behind","i need")):
        c.execute("INSERT INTO memories(session_id,memory) VALUES(?,?)",(s,msg[:1200]))
    c.commit();c.close()
    return jsonify(reply=reply,actions=actions,suggestion=suggestion)
if __name__=="__main__":app.run(host="0.0.0.0",port=int(os.environ.get("PORT","3000")))
