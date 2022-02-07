<p align="center">
	<a href="https://www.python.org/" target="_blank" alt="Picture of python with link to python.org">
        	<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=darkgreen">
	</a>
 	<hr />
</p>

![plot](https://abload.de/img/screenshot2022-02-072ahkp8.png)

***WARNING! THIS PROGRAM IS A WORK IN PROGRESS! ANYTHING CAN CHANGE AT ANY MOMENT WITHOUT ANY NOTICE! USE THIS PROGRAM AT YOUR OWN RISK!***

# py2bin - another PyInstaller wrapper.

During the planning phase for Project CMBFan, I decided that I would like to offer the option to run the project natively as a binary to avoid problems with python dependencies. In search of a solution I came across [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/), however, a problem arose quite quickly, this can only convert one file at a time with the respective standard imports, but if you use your own classes it becomes quite dark. So I googled further but found nothing right. So I decided to program a wrapper myself to meet my needs.

## What is py2bin

It's an Wrapper for the [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/), it converts all your pyton files in your src folder in one single binary file. You may think now, hey but project x from x can this too, but here comes an special, with my py2bin you can write .patch files to add patches during the generation of you binary.

## What py2bin does

- [x] Reading files in /src folder
- [x] Loading ech file into one build file
- [x] apply patches from .patch files in build/patches folder (Remove // Replace // Add - lines)
- [x] Gernerate an binary file with the usage of PyInstaller
- [x] Cleaning up directory from build/temp files
- [x] Logging all the stuff, i wrote all steps with logs so you will find any problem, the output of PyInstaller is also saved as log

![plot](https://abload.de/img/screenshot2022-02-072jqjnh.png)
You see only the output of INFO level here, there is an DEBUG level too

## What is ToDo

- [ ] Update Readme.md (adding screenshots)
- [ ] Cleaning up code
- [ ] Adding option to use arguments (to set outputname etc)
- [ ] Add function that rename the output binary to project name
- [ ] Adding options to set start positions for Replace in lines
- [ ] Adding missing stuff that will be get reported by you
- [ ] Fixing typos, bugs

# Usage

Clone the Repo or Download the binary from [release](). Because of wip, you need an src/ and build/ folder in your project. The src/ folder contains all your .py files. In the build/ directory you put the py2bin binary and your patches

## start the program
```bash
cd build/
./py2bin
```

## How an patchfile looks like?

Each line in an .patch file is an patchline, so if you had an hello_world.py you need an hello_world.patch. As example we wanne remove an line,add an line, replace an line and remove multiple lines.
```
RM%20
ADD%2%#This is an added commment by patch
RE%1%#!/bin/python3
RM%1%3
```

### Okay... how this works?

% is an separator, first comes the command (RM/RE/ADD) The commands should selfexplained. After that you enter an line number and than the input (in case of RE or ADD) if you add an second number on the RM command, than it will remove multiple line (from -> to).

To get no problems durring the patching i have sorted the work tasks, first we apply to manage the removing of lines, this way i avoid the problem that possibly added or replaced lines are deleted afterwards. All removed lines will be counted so that when patch "Add" will apply it will patch the right line.

# footer

I don't know how fast the future development go on, beceuase of Family and my daily job, i had no much time. Feel free to test it out and report bugs/issues.
