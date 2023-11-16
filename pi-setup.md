# Set up for the Raspberry Pi 5
>[!important]
> Make sure that you have read the [README.md](README.md) file before reading this file
## Initial setup
### Raspberry Pi Imager
Install Raspberry Pi OS using [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Put the SD card you'll use with your Raspberry Pi into the reader and run Raspberry Pi Imager.

Follow the on-screen instructions to select Device (Raspberry Pi 5), OS (Raspberry Pi OS 64-bit (Bookworm)) and click next.

Under additional options, ensure the following options are configured:

Username: pi

Password: raspberry

Enable SSH connections

Optional: Configure a wireless network (this isn't required if setting up with keyboard and mouse)

Press next and wait a couple minutes. Raspberry Pi Imager will automatically eject your SD card when done.

Insert the SD card into the Pi 5 and boot.

>[!important]
> If booted for the first time in 'headless mode' (no monitor, keyboard or mouse connected) then connect [via SSH](https://www.onlogic.com/company/io-hub/how-to-ssh-into-raspberry-pi/). Ensure working wireless connection from earlier steps.

### Initial Settings Configuration
Open terminal using keyboard and mouse, or connect via SSH.
Access the Raspberry Pi Configuration Menu using command:

    sudo raspi-config

Use keyboard arrows + Enter to navigate through the menus. Press tab to select options at bottom of the screen.
#### 1 System Options
S5 Boot / Autologin > B4 Desktop Autologin
#### 1 Display Options
D3 VNC Resolution > 1920 x 1080
#### 3 Interface Options
I1 SSH > Enable (if not enabled during imaging)
I2 VNC > Enable
I4 I2C > Enable
#### 6 Interface Options
A6 Wayland > W1 X11

### Enabling VNC (remote desktop) access
This will only work if Wayland has been changed to X11 desktop environment.
First, start vncserver in service mode:

    run systemctl start vncserver-x11-serviced.service

This will open the vncserver daemon. To enable vncserver on startup:

    run systemctl enable vncserver-x11-serviced.service

For more info on vncserver in service mode see [documentation](https://help.realvnc.com/hc/en-us/articles/360002310857#vncserver-x11-serviced-0-0).

Reboot:

    sudo reboot

Vncserver should open on boot and appear on the taskbar. Double click icon to open the UI. Under connections, sign in with realvnc details to enable cloud connectivity.

To remotely access, download [VNCviewer](https://www.realvnc.com/en/connect/download/viewer/) on your PC/Mac and login. Our RPi should appear under cloud connections.


### Installing software?
### Display setting to connect to it from other computers

## Python
### Installing the correct version of python for the project
`Python3.8` is the python version for this project, to install it the following steps need to be followed:

Steps can go here

### Creating a virtual environment
Make sure to create the virtual environment using desired python version and give a suitable name (such as `heroEnv`)

    python3.8 -m venv heroEnv

### Instalilng libraries
#### Global libraries
#### Virtual environment libraries
> [!important]
> Make sure that you have changed your current terminal directory to the folder created by the newly created virtual environment by "cd `heroEng`"

    cd<location>

Run the environment so that the libraries are all installed in it

    source bin/activate

> To exit the virtual environment run "deactivate" on the command line

We can the install the libraries needed by using pip
    
    pip3 install <package_name_1> <package_name_2> ...

The [packages needed](requirements.txt) for this project can be found [here](requirements.txt). For simplicity the following command can be run while on the workspace:

    python3 requirements.py

> The command above gives you a string that you can copy and paste to install all of the required packages for this project

## 😱 Fuck up? Reset the Pi (tada :tada:)

This still needs to be done

albert