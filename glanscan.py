import os.path
import socket
import subprocess
import sys
import gi
import threading

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Gdk, Adw
from time import sleep

# VERSION = 1.0.1
ver = "1.0.1"


# GLOBAL VARIABLES
global thread
global thread_started
thread_started = False

tbuffer = Gtk.TextBuffer()
entry_host = Gtk.Entry()
entry_iprange = Gtk.Entry()
button_ipscan = Gtk.Button(label="IP-Scan")
button_ipscan_stop = Gtk.Button(label="Stop")
statusbar = Gtk.Statusbar()

# STARTUP CHECKS

# CHECK IF THE NMAP COMMANDLINE TOOL IS INSTALLED
file = "/usr/local/bin/nmap"
if os.path.exists(file):
    print("Found the nmap binary. (CONTINUE)")
else:
    print("Can't find the nmap binary. It should be in /usr/local/bin/ (EXIT)")
    sys.exit(0)

def is_dark_mode_enabled():
    command = 'osascript -e "tell app \\"System Events\\" to tell appearance preferences to get dark mode"'
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = result.communicate()
    out = out.strip()
    if out == "true":
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", True)
    else:
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", False)

is_dark_mode_enabled()

# DEF - THREAD CLASS
class MyThread(threading.Thread):
    def __init__(self):
        super(MyThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            print("Thread is running...")
            sleep(10)

            global tbuffer
            global entry_iprange

            iprange = entry_iprange.get_text()

            if iprange != "" and ";" not in iprange:
                txt = ""
                txt = txt + "\n\tScan Report: \n"

                status = subprocess.Popen("/usr/local/bin/nmap -sn -PR " + iprange + " | grep report | cut -d\" \" -f5,6",
                                          shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, universal_newlines=True)
                rcstat = status.wait()
                out = status.communicate()
                txt_split = out[0].split("\n")
                x = 0
                while (x < len(txt_split)):
                    txt = txt + "\n\t" + txt_split[x]
                    x = x + 1

                txt = txt + "\n\tHosts Up: " + str(x - 1) + "\n"
                GLib.idle_add(tbuffer.set_text, txt)

        print("Thread stopped.")
        statusbar.push(0, "Done.")

        entry_iprange.set_sensitive(1)
        button_ipscan.set_sensitive(1)


def stop_thread(thread):
    global thread_started
    thread.stop()
    thread_started = False
    statusbar.push(0, "Stopping the scan ..., please wait.")
    button_ipscan_stop.set_sensitive(0)


# DEF - scan_lan
def scan_lan(obj):
    if entry_iprange.get_text() != "" and ";" not in entry_iprange.get_text():
        global tbuffer
        global thread
        thread = MyThread()

        tbuffer.set_text("\n\tScanning ..., please wait.")
        def start_thread():
            global thread_started
            if not thread_started:
                thread.start()
                thread_started = True
                statusbar.push(0, "Scanning the IP-ranning ..., please wait.")
                button_ipscan_stop.set_sensitive(1)

        GLib.idle_add(start_thread)

        entry_iprange.set_sensitive(0)
        button_ipscan.set_sensitive(0)

# DEF - start_portscan
def start_portscan(obj):
    global entry_host
    host = entry_host.get_text()
    x = 0
    try:
        # Attempt to resolve the address
        socket.inet_pton(socket.AF_INET, host)
        x = 1
    except socket.error:
        x = 0

    ogg = 0
    oga = 0

    if x == 1:
        title = "gLanScan - Scanning: " + host
        if os.path.exists("/usr/bin/ogg123"):
            ogg = 1
        if os.path.exists("/usr/share/sounds/Yaru/stereo/system-ready.oga"):
            oga = 1

        command = "osascript -e 'tell application \"Terminal\" to do script \"/usr/local/bin/nmap -T4 -p 1-65535 -sV " + host + "\"'"
        status = subprocess.Popen(command, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, universal_newlines=True)
        rcstat = status.wait()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        global thread
        thread = MyThread()

        win = MainWindow(application=app)
        win.set_title("gLanScan " + ver)
        win.set_default_size(500, 400)
        win.set_resizable(False)
        box0 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        win.set_child(box0)
        box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box0.append(box1)
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box0.append(box2)

        label_spacer = Gtk.Label()
        box2.append(label_spacer)

        box4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box2.append(box4)

        start_label1 = Gtk.Label(label="IP-range")
        start_label1.set_size_request(100, -1)
        box4.append(start_label1)

        global entry_iprange
        entry_iprange.set_max_length(40)
        #entry_iprange.connect("activate", scan_lan)
        box4.append(entry_iprange)

        global button_ipscan
        button_ipscan.set_size_request(100, -1)
        button_ipscan.connect("clicked", scan_lan)
        box4.append(button_ipscan)

        global button_ipscan_stop
        button_ipscan_stop.set_sensitive(0)
        button_ipscan_stop.set_size_request(100, -1)
        button_ipscan_stop.connect("clicked", lambda btn: stop_thread(thread))
        box4.append(button_ipscan_stop)

        label_spacer1 = Gtk.Label()
        box2.append(label_spacer1)

        scrolled_window = Gtk.ScrolledWindow()
        global tbuffer
        textview = Gtk.TextView.new_with_buffer(tbuffer)
        scrolled_window.set_size_request(500, 300)
        textview.set_buffer(tbuffer)
        textview.set_editable(False)
        textview.set_wrap_mode(Gtk.WrapMode.NONE)
        scrolled_window.set_child(textview)
        box2.append(scrolled_window)

        label_spacer = Gtk.Label()
        box2.append(label_spacer)

        box3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box2.append(box3)

        start_label = Gtk.Label(label="Host")
        start_label.set_size_request(100, -1)
        box3.append(start_label)

        global entry_host
        entry_host.set_max_length(20)
        #entry_host.connect("activate", start_portscan)
        box3.append(entry_host)

        button_portscan = Gtk.Button(label="Scan")
        button_portscan.set_size_request(100, -1)
        button_portscan.connect("clicked", start_portscan)
        box3.append(button_portscan)

        label_spacer1 = Gtk.Label()
        box2.append(label_spacer1)

        global statusbar
        box2.append(statusbar)

        statusbar.push(0, "Ready.")
        tbuffer.set_text("\n\tEnter an IP-range to start a scan.")

        win.present()


app = MyApp(application_id="com.sprokkel78.glanscan")
app.run(None)
