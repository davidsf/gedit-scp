from gi.repository import GObject, Gedit, Gdk, Gio, Gtk, PeasGtk, GLib
import subprocess
import os
import time
import re

SETTINGS_SCHEMA = "org.gnome.gedit.plugins.scp"

# UI manager snippet to add menu items to the View menu
ui_str = """
<ui>
  <menubar name="MenuBar">
    <menu name="ViewMenu" action="View">
      <placeholder name="ViewOps_2">
        <separator/>
        <menuitem name="ScpUpload" action="ScpUploadAction"/>
        <separator/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""
class ScpAppPlugin(GObject.Object, Gedit.AppActivatable, PeasGtk.Configurable):
  app = GObject.property(type=Gedit.App)

  def __init__(self):
    GObject.Object.__init__(self)

  def do_activate(self):
    pass

  def do_create_configure_widget(self):
    widget = Gtk.Table(1,2,False)
    label = Gtk.Label("Server:")
    entry = Gtk.Entry()
    settings = Gio.Settings.new(SETTINGS_SCHEMA)
    server = settings.get_string('server') 
    entry.set_text(server)
    entry.connect('key-press-event', self.on_key_press_event)
    widget.attach(label, 0, 1, 0, 1)
    widget.attach(entry, 1, 2, 0, 1)
    widget.set_border_width(6)
    return widget

  def on_key_press_event(self, widget, event):
    txt = widget.get_text()
    settings = Gio.Settings.new(SETTINGS_SCHEMA)
    settings.set_value('server', GLib.Variant("s", txt))

  def do_deactivate(self):
    pass

  def do_update_state(self):
    pass

class ScpWindowPlugin(GObject.Object, Gedit.WindowActivatable):
  __gtype_name__ = "ScpPlugin"
  window = GObject.property(type=Gedit.Window)
    
  def __init__(self):
    GObject.Object.__init__(self)

  def do_activate(self):
    icon = Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.MENU)
    sw = Gtk.ScrolledWindow()
    self.textarea = Gtk.TextView()
    panel = self.window.get_bottom_panel()
    panel.add_item(self.textarea, "ScpBottomPanel", "Scp Upload", icon)
    panel.activate_item(self.textarea)

    self._insert_menu()

    self._accel_group = Gtk.AccelGroup()
    self.window.add_accel_group(self._accel_group)

    if not isinstance('scp-upload', Gtk.Action):
      action = self._action_group.get_action('scp-upload')

    if not action:
      return

    self._accel_group.connect_group(Gdk.KEY_U, Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK, Gtk.ACCEL_LOCKED, self.upload)

    self.window.set_data("Scp", handlers)

  def upload(self, group):
    tab = self.window.get_active_tab()
    document = tab.get_document()
    filename = document.get_uri_for_display()
    panel = self.window.get_bottom_panel()
    panel.activate_item(self.textarea)
    visible = panel.get_property("visible")
    panel.set_property("visible", True)
    settings = Gio.Settings.new(SETTINGS_SCHEMA)
    server = settings.get_string('server') 

    # get root
    base = 'org.gnome.gedit.plugins.filebrowser'
    settings = Gio.Settings.new(base)
    root = settings.get_string('virtual-root')
    if root is not None:
	root = re.sub(r'^file://','', root)
	dest = re.sub(root+'/', '', filename)
	
    p = subprocess.Popen("scp " + filename +" "+server+'/'+dest, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    txt = "'%s' uploading " % dest
    self.addtext(self.textarea, txt)
    while p.poll() is None: 
	while Gtk.events_pending():
		Gtk.main_iteration()
        self.addtext(self.textarea,".")
	time.sleep(0.1)
    if p.returncode == 0:
    	self.addtext(self.textarea,"success\n")
    else:
    	self.addtext(self.textarea,"Error: "+p.stderr.read()+"\n")
    while Gtk.events_pending():
	Gtk.main_iteration()
    time.sleep(1)
    panel.set_property("visible", visible)



  def do_deactivate(self):
    self._accel_group = None
    self._action_group = None

  def do_update_state(self):
    pass

  def _insert_menu(self):
    # Get the GtkUIManager
    manager = self.window.get_ui_manager()

    # Create a new action group
    self._action_group = Gtk.ActionGroup("GeditTextSizePluginActions")
    self._action_group.add_actions([("ScpUploadAction", None, _("_Upload to SFTP"),
                                     "<Ctrl><Alt>U", None,
                                     self.upload)])

    # Insert the action group
    manager.insert_action_group(self._action_group)

    # Merge the UI
    self._ui_id = manager.add_ui_from_string(ui_str)

  def addtext(self, TV,text):
    buffer = TV.get_buffer()
    iter = buffer.get_iter_at_mark(buffer.get_insert())
    buffer.insert(iter,text)   # use "\n" for newlines


