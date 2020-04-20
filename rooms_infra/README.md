# team79

## login.py
**When?** Should be used as soon as the ESP turns on, in the setup method. <br>
**How?** POST request to login.py with a 'username' argument. <br>
**Returns:** ```"Hello user "+username+", you are online!"```

## ping.py
**When?** Every 10 seconds. If the server doesn't receive a ping in 30 seconds, it assumes the ESP has turned off/disconnected and makes appropriate actions. <br>
**How?** POST request to ping.py with a 'username' argument. <br>
**Returns:** ```"1"``` if nothing to change, but ```"0"``` if they need to be in the main menu (either they are already there and that's fine, or the host has just left and they have been kicked out to the main menu).

## host_room.py
**When?** Should be used whenever a user wants to host a new room.<br>
**How?** POST request to host_room.py with 'username' and 'game_id' arguments. game_id should be one of the keys of GAME_ID_TO_NAME, as defined below (string is okay). <br>
**Returns:** ```"Welcome to room " + str(room_id) + ".\n" + "You are playing game " + GAME_ID_TO_NAME[str(game_id)]+"."```

## join_room.py
**When?** Two uses, either to get all rooms or join a room (and the game, immediately). <br>
#### Get all available rooms
**How?** GET request to join_room.py with no arguments. <br>
**Returns:** ```room_id + ", hosted by " + host + ", capacity " + capacity + ", game: " + GAME_ID_TO_NAME[game_id]``` for each room, separated by a new line ```\n``` character.
#### Join a room
**How?** POST request to join_room.py with a 'username' and 'room_id' argument. <br>
**Returns:** ```"Welcome to room" + room_id + ". The host is" + host + "\n" + "Here, the activity is " + GAME_ID_TO_NAME[game_id]``` OR ```"Invalid room id!"```

## leave_room.py
When? Should be used when the user wants to leave the room and go back to main screen.  NOTE: If they are the host, it will kick everyone else out of the room, within 10 seconds.<br>
How? POST request to leave_room.py with a 'username' argument. <br>
Returns: ```"You have successfully left the room."```

## Extra defaults:
```
GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "Tichu"}
```
