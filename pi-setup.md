# Set up for the Raspberry Pi 5
>[!important]
> Make sure that you have read the [README.md](README.md) file before reading this file
## Initial setup
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