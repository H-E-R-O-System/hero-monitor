# Setting up github on the terminal (through SSH key)
## Generating a new SSH key
More detail on this can be found [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

Open terminal and run the following command

    ssh-keygen -t ed25519 -C "your_email@example.com"

>[!note]
> If you are using a legacy coputer, use:
> ```ssh-keygen -t rsa -b 4096 -C "your_email@example.com"```

You can press enter 3 times to skip the next few steps

## Adding your SSH key to the ssh-agent
Run the following commands

    eval $(ssh-agent -s)

then

    ssh-add ~/.ssh/id_rsa

Next open the file and copy the key inside of it

    open ~/.ssh/id_rsa.pub

>[!note]
> If you are on mac you can simply run `pbcopy < ~/.ssh/id_rsa.pub`. Which will copy the components of the file instead

You can the go to to `github > settings > SSH and GPG keys > New SSH key` and add paste the key into the key box (save and you should now have access to github)