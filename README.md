# PY-NanoShell
Basic logic to implement a command shell using python3. This way, you can create your own with a simple setup.

## How to setup:
1. Create a new file with the name of your shell. You can use the example file as a template.
2. Add the commands you want to use in the *CMDS* dictionary. Keep in mind that the commands can have multiple aliases.
3. Define the flags in the *FLAGS* dictionary.
4. Define the usage in the *USAGE* dictionary. Remember that mandatory elements are marked with <>, optional elements are marked with [] and that you can use the | operator to separate multiple options.
5. Define the description in the *DESCRIPTION* dictionary. This is the text that will be shown when the user uses the help command.
6. Define the constructor with the desired title that you want.
7. Extend the method ```_handle_cmd()``` to handle the commands. This is achieved by using a if-elif-else concatenation (switch statements may not work with all python versions). Remember that this function must return True if command found and False otherwise.
	- In order to keep the logic organized, you can call an auxiliar method for each command. This way, the validation and logic can be done there to keep the code clean.
8. Customize the title of the shell by modifying the ```_title()``` method.
9. **Enjoy your new shell!**

## Features:
- [x] Command aliases.
- [x] Autocompletion with the tab key.
- [x] Exit with Ctrl+D, Ctrl+C or the exit command.
- [x] You can use the arrow keys to navigate through the command, being able to edit it at any point.
- [x] History system to navigate through the commands you have used. Use the arrow keys to navigate through the history or use the command to list the history.
- [x] Log system storing the content of the shell in a file.
- [x] Modular design to allow the implementation of new commands.