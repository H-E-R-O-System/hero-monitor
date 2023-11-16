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

Python3.10 is the python version for this project, to install it the following steps need to be followed:

A few other programs and packages are needed to make sure the installation goes smoothly. Run the following on the terminal:

    sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev

Change the directiory to the downloads folder to download the python version

    cd ~/Downloads

Download python 3.10.13

    wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz`

Extract the downloaded file

    sudo tar zxf Python-3.10.13.tgz

Go into the new extracted folder

    cd Python-VERSION

and configure the new the source files for building

    sudo ./configure --enable-optimizations

Run (4 being the number of core to be used)

    sudo make -j 4

Finally, install python by running this command

    sudo make altinstall

>[!note]
> You can check if the version has been installed properly by typing `python3.10 --version`

### Installing packages
#### Virtual environment libs
Change the directory back to the home directiory to create a virutal environment

    cd ~

Create a virtual environment using python 3.10.13 and name it (for example HEROenv)

    python3.10 -m venv HEROenv

Run the environment so that the libraries are all installed in it

    source HEROenv/bin/activate

> [!important]
> For future times, when activating the envionment make sure to be within the folder `cd HEROenv` and then running `source bin/activate` to run the environment

To exit the virtual environment run `deactivate` on the terminal

Next the [required packages](requirements.txt) can be installed using the following commmand `pip3 install numpy scipy...`

For simplicity the following command can be run while on the workspace:

    python3 requirements.py

copy and paste the output given by that file to install all the pre-requisits

## 😱 Fuck up? Reset the Pi (tada :tada:)

This still needs to be done