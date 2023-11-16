with open('requirements.txt') as f:
    # read all the requirements needed
    lines = f.readlines()
    # remove versions
    packages = [i.split("~")[0] for i in lines]
    # create the string
    string = " ".join(packages)
print()
print(" The following packages will be needed ".center(70, "#"))
print()
for package in lines:
    print(package)
# close file and print the output
print()
print(" To intsall them simply run ".center(70, "#"))
print()
print("pip3 install " + string)