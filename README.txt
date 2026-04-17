Echoes of the Forgotten Station

A text-based sci-fi adventure game built in Python.

Features
- Object-Oriented Programming
- Rule-Based AI difficulty system
- Inventory 
- Combat system
- JSON save/load
- SQLite database tracking game history
- Multiple endings
- Search the Rooms to find your active and passive items
- This branch Includes an extra gui based menu

libraries used 
 - SQLite - the sqlite code is taking directly from online 
 - JSON
 - 

AI behavior 
 - player takes enough damage and gets directed to medical
 - player wins enough fights and the enemies get stronger
 - player explores enough rooms and the game gives teh hint to search the rooms 

items so Far 
 - prybar = used to open secret hatch and security locker
 - medkit = healing 
 - access card = used to shut down AI core 

Endings 
 - Survivor 
 - Savior
 - Narrow Escape
 - Death 
 - Total destruction 

In Game Commands: 
move north
move south
move east
move west

look
take ITEM
use ITEM
status
save
load
map
quit

to run the game enter "python main.py" 

The project includes ideas and concepts not yet covered in class due to 
me going online and looking up tutorials and guides for game development 

that is the reason why this project is seperated into seperate python files
i read that it was good design 

i used the python wiki under the Game Programming section
https://wiki.python.org/moin/GameProgramming
this led me to different tutorials and python lessons i used to make this
project just a little better

Known limitations 
 - i dont really know of any limitations since the program was designed to be expandable 

Future improvements (as of writing this)
 - keys for doors such as needing a key to enter the ai room 
 - more items such as weapons, make the fights more difficult so that you have to use weapons to win 
 - allow medkit to be used during fights
 - convert this from a terminal game to a windowed game


I do not know if any part of my project is copied from the internet 
there is a high chance peices of it will be similiar to other projects 
but thats just what happens when you learn from tutorials and other easily available sources