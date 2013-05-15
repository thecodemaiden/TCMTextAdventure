#globals/names

ENV_APPEAR = "APPEAR"
ENV_SMELL = "SMELL"
ENV_ABOVE = "ABOVE"
ENV_BELOW = "BELOW"

env_properties = [ENV_APPEAR, ENV_SMELL, ENV_ABOVE, ENV_BELOW]

DIR_NORTH = "N"
DIR_SOUTH = "S"
DIR_EAST = "E"
DIR_WEST = "W"
DIR_UP = "U"
DIR_DOWN = "D"
DIR_LEFT = "L"
DIR_RIGHT = "R"
DIR_FORWARD = "F"
DIR_BACKWARD = "B"

directions = [DIR_NORTH, DIR_SOUTH, DIR_EAST, DIR_WEST, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_FORWARD, DIR_BACKWARD]
compass_directions = [DIR_NORTH, DIR_SOUTH, DIR_EAST, DIR_WEST]

OBJ_KEY = "key"
OBJ_CLEAVER = "cleaver"
OBJ_CANDLE = "candle"
OBJ_DRESSER = "dresser"
OBJ_GRINDSTONE = "grindstone"
OBJ_LIGHTER = "lighter"
OBJ_WINDOW = "window"
OBJ_OVEN = "oven"
OBJ_WD40 = "spray"
OBJ_NOTE = "note"
OBJ_COMPASS = "compass"
OBJ_DOOR = "door"
OBJ_OVEN = "oven"

object_names = [OBJ_KEY, OBJ_CLEAVER, OBJ_CANDLE, OBJ_DRESSER, OBJ_GRINDSTONE, OBJ_LIGHTER, OBJ_WINDOW, OBJ_OVEN, OBJ_WD40, OBJ_NOTE, OBJ_COMPASS, OBJ_DOOR, OBJ_OVEN]


# later we can add room names and a 'go to room' command

RM_KITCHEN = "kitchen"
RM_LIVING = "living room"
RM_BATH = "bathroom"
RM_CLOSET = "closet"
RM_BED = "bedroom"
RM_FOYER = "foyer"
RM_ATTIC = "attic"

room_names = [RM_KITCHEN, RM_LIVING, RM_BATH, RM_CLOSET, RM_BED, RM_FOYER, RM_ATTIC]

#{player facing dir: (relative,absolute)}
# not a dict because i need reverse lookup for room descriptions without compass
direction_matrix = {DIR_NORTH: [(DIR_FORWARD, DIR_NORTH), (DIR_BACKWARD, DIR_SOUTH), (DIR_LEFT, DIR_WEST), (DIR_RIGHT, DIR_EAST)],
			DIR_SOUTH: [(DIR_FORWARD, DIR_SOUTH), (DIR_BACKWARD, DIR_NORTH), (DIR_LEFT, DIR_EAST), (DIR_RIGHT, DIR_WEST)],
			DIR_WEST: [(DIR_FORWARD, DIR_WEST), (DIR_BACKWARD, DIR_EAST), (DIR_LEFT, DIR_SOUTH), (DIR_RIGHT, DIR_NORTH)],
			DIR_EAST: [(DIR_FORWARD, DIR_EAST), (DIR_BACKWARD, DIR_WEST), (DIR_LEFT, DIR_NORTH), (DIR_RIGHT, DIR_SOUTH)]}

gas_conc = 1.0 # diminishes if oven is off and windows are open, increases otherwise
windows_open = False 
gas_off = False

def player_to_compass(dir, facing):
    if facing in direction_matrix:
        options = direction_matrix[facing]
        for pair in options:
	    if (pair[0] == dir):
		return pair[1] 
    return dir

def compass_to_player(dir, facing):
    if facing in direction_matrix:
	options = direction_matrix[facing]
	for pair in options:
	    if (pair[1] == dir):
		return pair[0]
    return dir

def article_obj(s):
    if s[0] in ['a', 'e', 'i', 'o', 'u']:
        return "an "+s
    else:
        return "a "+s

def object_list_text(objects):
    s = "nothing"
    if len(objects) > 0:
	s = ", ".join([article_obj(x.name.lower()) for x in objects])
	open_objs = [o for o in objects if o.is_open]
	if len(open_objs) > 0:
	    s += "\n"
	for o in open_objs:
	    contents_list = object_list_text(o.contents)
	    s += "In the " + o.name + " you see " + contents_list
    return s

def display(s):
    print s

