from cx_Freeze import setup,Executable
import py2exe
includefiles = ['codenames_blank_temp.jpg', 'board.py', 'word_list.txt', 'Codenames_server.py', 'Codenames_client.py', 'Codenames.py']

build_exe_options = {"packages": ["os", "re", "PIL", "pickle", "random", "email", "smtplib", "ssl", "pygame", "socket", "threading", "sys"], "excludes": ["tkinter", "doctest", "pdb", "unittest", "difflib", "inspect", ], 'include_files':includefiles}

setup(
    name = 'Codenames',
    version = '1.0',
    description = 'Fan version of Codenames',
    author = 'Noam ELisha',
    options = {"build_exe": build_exe_options}, 
	executables = [Executable(script="menu.py", base="Win32GUI", targetName="Codenames.exe")]
)