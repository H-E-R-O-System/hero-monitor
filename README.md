# The H.E.R.O. System – A framework for neurodegenerative disease monitoring 🤖

## Project Description

## Setting up the environment - Mac

### Step 1: Ensure that portaudio is installed

    % brew install portaudio 

### Step 2: install dependencies as given in **`requirements.txt`**

if getting clang error when installing **`PyAudio`** make sure latest software is installed 

    % softwareupdate --all --install --force

and then run to install the latest set of command line tools

    % sudo rm -rf /Library/Developer/CommandLineTools
    % sudo xcode-select --install


sentencepiece
protobuf

### Some useful comands while using git
```commandline
git fetch --all
git reset --hard origin/main

# force git push 
git -c credential.helper= -c core.quotepath=false -c log.showSignature=false push --force
```

