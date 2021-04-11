# Lua Dissector Generator (LuDis)

## Introduction

This tool is the empirical part of the Master's thesis titled "A tool for generating protocol dissectors for Wireshark in Lua", which was conducted in the Department of Computer Science and Engineering, at the University of Oulu, Finland. The tool was developed in order to make it possible for people
with little or no experience in programming to create protocol dissectors and to
make the creating of dissectors for new protocols faster and easier.

The thesis can be found in this repository or in Jultika publication archive at: http://urn.fi/URN:NBN:fi:oulu-201312021942

The principal functionality of LuDis is to generate Wireshark dissectors in Lua
according to the protocol rules defined by the user. The rules are specified basically by opening a sample packet of the protocol with the tool and defining all fields of the packet.

## Usage

LuDis requires version 2 of the Python interpreter to be installed. Tkinter toolkit should be bundled with the interpreter installation. The main module is the `ludis.py` so the program can be started by running `python ludis.py` in the command line.

The program has a brief manual in itself (*help.txt* in the source files) and it has quite a few error/info popups that will guide the user in doing the right things. The attached sample input files might help you in getting familiar with the tool. There's even a memo (*demo_memo.pdf*) I used when demonstrating the tool to my thesis supervisor, the resulting dissector files (in Lua) and packet captures for testing the dissectors in Wireshark.

For more detailed description and usage instructions, see the section 6 of the thesis.


## Afterword

I hope the tool will be of help to you, for example, when working with your own custom protocol, and save your time from writing dissectors to other things. Any kind of feedback is welcomed and you can send it via [OUSPG](https://www.oulu.fi/bisg/ouspg) (Oulu University Secure Programming Group).
