# Set up for the Raspberry Pi 5
>[!important]
> Make sure that you have read the [README.md](README.md) file before reading this file
## Initial setup jamie 
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