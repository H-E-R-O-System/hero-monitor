# H.E.R.O-System

## Setting up the environment - Mac
For Mac users make sure to run

### Step 1: Ensure that portaudio is installed

    % brew install portaudio 

### Step 2: install dependencies as given in **`requirements.txt`**

if getting clang error when installing **`PyAudio`** make sure latest software is installed 

    % softwareupdate --all --install --force

and then run to install the latest set of command line tools

    % sudo rm -rf /Library/Developer/CommandLineTools
    % sudo xcode-select --install

