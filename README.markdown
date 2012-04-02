Gedit SCP
=========

This is a plugin for [Gedit][2], the official text editor of the GNOME desktop
environment. This plugin is for Gedit versions 3 and above. **This plugin is NOT
compatible with Gedit 2.x**.

With the keyboard shortcut [Ctrl]+[Alt]+u will upload the current open document to the target server and directory setup in the preferences configuration dialog.

Installation
------------

1. Download the source code form this repository or using the `git clone` command.
2. Copy the files to the Gedit plugins directory `~/.local/share/gedit/plugins/`.
3. Copy and compile the settings schema **as root**.
4. Restart Gedit.
5. Activate the plugin in the Gedit preferences dialog.

### For Example...

    git clone git://github.com/davidsf/gedit-scp.git
    cp scp* ~/.local/share/gedit/plugins/
    
**With root access** (`su` or `sudo`)...

    cp org.gnome.gedit.plugins.scp.gschema.xml /usr/share/glib-2.0/schemas/
    glib-compile-schemas /usr/share/glib-2.0/schemas/

[2]: http://www.gedit.org
