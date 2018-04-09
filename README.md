# dim
[Imgur](https://i.imgur.com/4PFgSr6.png)
## How to run
Navigate to `.../dim/src`  
`python3 main.py`

## Usage!

### Movement 

#### Basic movement
Super similar to `vim` bindings, so if you use `vim` bindings a lot you'll be (mostly) right at home!
* `j` to move down
* `k` to move up
* `l` to move right
* `h` to move left

#### Switching to other states from normal
* `i` to enter `INSERT` mode
* `a` to move right one character and enter `INSERT` mode
* `A` to move to the end of the current line, move right one character and enter `INSERT` mode
* `v` to enter `VISUAL` mode
    * Not implemented yet!
* `:` to enter `CMD_LINE` mode
* `\`` to enter `FILE_NAV` mode
* `.` to enter `OPTIONS` mode

#### More advanced features
* `w` to jump forward a word and then the whitespace in front of the word
* `e` to jump forward a word
* `b` to jump backward a word
* `g` to jump to the beginning of the file
* `$` to jump to the end of the current line
* `0` to jump to the beginning of the current line
* `x` to delete the current character under the cursor
* `d` to move to delete mode
    * any movement command following `d` will delete instead of move the cursor
    * `dd` will delete the current line
    * `dw` will delete the next word and whitespace in front of the word
    * `db` will delete the previous word
* Any numbers to do an operation multiple times. A couple of examples are below:
    * `75g` to jump to the 75th line
    * `3w` to jump forward 3 words (including whitespace at the end)
* Deletion and numbers can be combined. Examples below:
    * `d3w` deletes the next 3 words (and whitespace)
* `/` to search for a substring in the current text and store it in a buffer
    * `n` to cycle through the search buffer

### Other features accessed from Normal mode
* `u` while in Normal mode to undo
* `ctrl+r` while in Normal mode to redo

### Insert Mode
Type as normally! To exit insert mode and go back to `NORMAL` mode, press `ESC`.

### Command Line Mode
Entering command line mode will bring you to the line at the bottom of the editor and you can enter in a command below.  
Available commands are:
* `q` to quit the editor
* `w` to save the currently edited file
    * `w fileName` to save a file with name fileName within the current directory
* `wq` to save and exit
* `!` with some other commands to run them in terminal
    * `!ls` will perform the `ls` command and output to `dim`
    * `!python3 FILENAME.py` will run FILENAME.py with the python3 interpreter

### File navigation
When in `NORMAL` mode, press `\`` to enter `FILE_NAV` mode.  
(Picture of what this looks like coming soon!)  
Folders are colored in a cyan like color in default color scheme, and files are a middle grey color.

#### File navigation subscreen movement
* `j` to move down
* `k` to move up
* `?` to enter a searching submode. Enter in any prefix of a file you want to search for, and if there's anything in the current directory that matches the characters to the beginning it will move your cursor to that point.
* Press `\`` to go back to `NORMAL` mode.

#### Directory movement
* Press enter to go to the directory selected, or if it's a file it will open it in the text editor.

