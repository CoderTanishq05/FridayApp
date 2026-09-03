from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
import math, os, threading, time, datetime
Window.clearcolor = (0,0,0,1)
AI_NAMES = ["friday", "jarvis", "buddy"]
def speak(t):
    print("FRIDAY:", t)
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
            Locale = autoclass('java.util.Locale')
            def _s():
                tts = TextToSpeech(PythonActivity.mActivity, None)
                time.sleep(0.3)
                tts.setLanguage(Locale.US)
                tts.speak(t, TextToSpeech.QUEUE_FLUSH, None, None)
            threading.Thread(target=_s, daemon=True).start()
        except: pass
def open_any_app(name):
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            pm = PythonActivity.mActivity.getPackageManager()
            name = name.lower().strip()
            packages = pm.getInstalledApplications(0)
            for pkg in packages:
                try:
                    label = pm.getApplicationLabel(pkg).toString().lower()
                    if name in label or label in name:
                        intent = pm.getLaunchIntentForPackage(pkg.packageName)
                        if intent:
                            PythonActivity.mActivity.startActivity(intent)
                            speak(f"Opening {label} sir")
                            return True
                except: pass
        except Exception as e: print(e)
    try:
        os.system(f"am start -p {name}")
        speak(f"Opening {name}")
        return True
    except: return False
def handle_command(raw_cmd, ui_label):
    raw = raw_cmd.lower()
    called_name = None
    for n in AI_NAMES:
        if n in raw:
            called_name = n
            raw = raw.replace(n, "").strip()
            break
    if not raw:
        if called_name:
            speak(f"Yes sir? {called_name} here")
            ui_label.text = f"{called_name.upper()} HERE\nListening..."
            return
        else:
            speak("Yes sir?")
            return
    cmd = raw
    if "time" in cmd:
        t = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"It's {t} sir")
        ui_label.text = f"Time: {t}"
        return
    if "open" in cmd:
        app_name = cmd.split("open")[-1].strip()
        for w in ["the", "app", "please", "sir"]:
            app_name = app_name.replace(w, "").strip()
        if app_name:
            if open_any_app(app_name):
                ui_label.text = f"Opening {app_name}"
            else:
                speak(f"Couldn't find {app_name}")
        return
    speak(f"You said {cmd}")
    ui_label.text = f"You: {cmd}"
class FridaySiri(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.phase=0
        self.listening=False
        with self.canvas:
            Color(0.255, 0.412, 0.882, 0.07)
            self.glow3 = Ellipse(size=(500,500), pos=(0,0))
            Color(0.831, 0.686, 0.216, 0.08)
            self.glow2 = Ellipse(size=(400,400), pos=(0,0))
            Color(0.4, 0.5, 0.95, 0.13)
            self.glow1 = Ellipse(size=(300,300), pos=(0,0))
            Color(0.831, 0.686, 0.216, 0.9)
            self.core = Line(width=2.2, close=True)
            Color(0.255, 0.412, 0.882, 0.85)
            self.outer = Line(width=2.8, close=True)
            Color(1, 0.92, 0.5, 0.6)
            self.hl = Line(width=1.2, close=True)
        self.info = Label(text="F.R.I.D.A.Y\nTAP TO TALK\nSay: Friday / Jarvis / Buddy", font_size=15, halign='center', color=(0.9,0.85,0.6,1), pos_hint={'center_x':0.5,'center_y':0.14})
        self.add_widget(self.info)
        Clock.schedule_interval(self.animate, 1/60)
    def siri_shape(self, cx, cy, base, offset, speed):
        pts=[]
        for i in range(60):
            ang = (i/60)*2*3.14159
            w1 = math.sin(ang*2 + self.phase*speed*0.8 + offset)*12
            w2 = math.sin(ang*3 + self.phase*speed*1.2 + offset*1.5)*8
            rip = math.sin(ang*5 + self.phase*speed*3)*(6 if self.listening else 2)
            r = base + (w1+w2+rip)*(0.8 if self.listening else 0.4)
            r *= 1.0 + math.sin(self.phase*0.7)*0.08
            pts.extend([cx+math.cos(ang)*r, cy+math.sin(ang)*r])
        return pts
    def animate(self, dt):
        self.phase += dt*(2.5 if self.listening else 0.9)
        w,h = Window.width, Window.height
        if w<10: return
        cx,cy = w/2, h/2+30
        breathe = 1.0 + math.sin(self.phase*0.7)*0.1
        self.core.points = self.siri_shape(cx, cy, 65*breathe, 0, 1.0)
        self.outer.points = self.siri_shape(cx, cy, 95*breathe, 3.14, 0.8)
        self.hl.points = self.siri_shape(cx, cy, 110*breathe, 1.57, 0.6)
        for j,g in enumerate([self.glow1, self.glow2, self.glow3]):
            gs = (300+j*100)*breathe
            g.size=(gs,gs); g.pos=(cx-gs/2, cy-gs/2)
    def on_touch_down(self, touch):
        self.listening=True
        self.info.text="Friday Listening..."
        self.listen()
        Clock.schedule_once(lambda dt: setattr(self,'listening',False), 4.5)
        Clock.schedule_once(lambda dt: setattr(self.info,'text',"F.R.I.D.A.Y\nTAP TO TALK\nSay: Friday / Jarvis / Buddy"), 4.5)
        return True
    def listen(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                from android import activity
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                RecognizerIntent = autoclass('android.speech.RecognizerIntent')
                intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Friday is listening sir")
                intent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 3500)
                intent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS, 4000)
                def on_result(req,res,data):
                    self.listening=False
                    if res==-1 and data:
                        results=data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                        if results:
                            raw_cmd=str(results.get(0))
                            self.info.text=f"You: {raw_cmd}"
                            handle_command(raw_cmd, self.info)
                            Clock.schedule_once(lambda dt: setattr(self.info,'text',"F.R.I.D.A.Y\nTAP TO TALK\nSay: Friday / Jarvis / Buddy"), 4)
                            return
                    self.info.text="Say again sir"
                    Clock.schedule_once(lambda dt: setattr(self.info,'text',"F.R.I.D.A.Y\nTAP TO TALK\nSay: Friday / Jarvis / Buddy"), 2)
                    try: activity.unbind(on_activity_result=on_result)
                    except: pass
                activity.bind(on_activity_result=on_result)
                PythonActivity.mActivity.startActivityForResult(intent, 1)
            except Exception as e: print(e)
class FridayApp(App):
    def build(self):
        Clock.schedule_once(lambda dt: speak("Friday online sir"),1)
        return FridaySiri()
FridayApp().run()