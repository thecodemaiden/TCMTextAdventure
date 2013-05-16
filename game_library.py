from random import randrange
from game_constants import *

class Player(object):
    def __init__(self):
        self.inventory = []
        self.current_room = None
        self.facing = DIR_WEST
        self.found_trapdoor = False
        self.is_dead = False
        self.is_escaped = False

    def travel(self, dir):
        if dir not in compass_directions and dir != DIR_UP and dir != DIR_DOWN:
	        dir = player_dir_to_compass(dir, self.facing)                
	else:
                dir = None
        if dir is None:
	        display("I don't know how to go there.")
        if dir in self.current_room.exits:
            newRoom = self.current_room.exits[dir]
            self.current_room = newRoom
            newRoom.onEntered()
    
    def die_now(self, death_message):
        display(death_message)
        self.is_dead = True

    def escape(self, escape_message):
        display(escape_message)
        self.is_escaped = True

    def has_compass(self):
      	l = [x for x in self.inventory if x.name == OBJ_COMPASS]
        return len(l) > 0

    def enter(self, room, monster):
        self.current_room = room
        room.onEntered(self, monster)


class Room(object):
    def __init__(self, name):
        self.objects = []
        self.exits = {}
        self.name = name
        self.dir_preambles = {DIR_NORTH: "To the north is the ", DIR_SOUTH: "To the south is the ",
			      DIR_WEST: "To the west is the ", DIR_EAST: "To the east is the ",
			      DIR_UP: "Above you is the ", DIR_DOWN: "Below you is the",
			      DIR_LEFT: "To your left is the ", DIR_RIGHT: "To your right is the ",
			      DIR_FORWARD: "Ahead of you is the ", DIR_BACKWARD: "Behind you is the "}

    def list_exits(self, use_relative=True, facing=None, include_updown=True):
        text_list = []
        look_directions = compass_directions[:]
        if include_updown:
            look_directions += [DIR_UP, DIR_DOWN]
        for direction in look_directions:
            desc = self.get_exit_descr(direction, use_relative, facing)
            if desc is not None:
                text_list.append(desc)
        if len(text_list) > 0:
            return " ".join(text_list)
        else:
            return "There are no exits. You are trapped."

    def get_exit_descr(self, direction, use_relative, facing):
        s = None
        try:
            room_name = self.exits[direction].name
            if use_relative:
                direction = compass_to_player(direction, facing)
            s = (self.dir_preambles[direction]+room_name+".")
        except KeyError:
            pass
        return s

    def smell_description(self):
        if (gas_conc >= 1.5):
            return "The smell of propane is almost overwhelming now."
        elif (gas_conc > 0.15):
            return "You smell propane, but it's not clear where it's coming from."
        else:
            return "You smell nothing."

    def place_object(self, obj):
        if obj.current_room is not None:
            try:
                obj.current_room.objects.remove(obj)
            except ValueError:
                pass
        obj.current_room = self
        self.objects.append(obj)

    def get_description(self, aspect, player, monster):
        #player is optional, mostly for when we 'gain knowledge'
        #monster lets us do noises based on monster positions

        s = None

        if aspect == ENV_APPEAR:
            s = "You are in the "+self.name +"."
            s += (" You see here: "+object_list_text(self.objects)+".")
            if monster.is_nearby(player):
                s += " You hear a faint scratching."
            if gas_conc > 0.1:
                s += " You smell something strange."
        elif aspect == ENV_SMELL:
            s = self.smell_description()
        elif aspect == ENV_ABOVE:
            s = "There is nothing interesting about the ceiling."
        elif aspect == ENV_BELOW:
            s = "There is nothing interesting about the floor."
        return s

    def onEntered(self, player, monster):
        print self.objects
        display(self.get_description(ENV_APPEAR, player, monster))
        display(self.list_exits(not player.has_compass(), player.facing, player.found_trapdoor))
		

class Item(object):
    def __init__(self, name):
        self.in_inv = False # not really necessary, but I'll leave it for now
        self.current_room = None        
        self.name = name
        self.is_portable = True
        self.is_open = False
        self.contents = []

    def use(self, player=None, others=[]):
        # args are other objects used with it
        pass 

    def describe(self, player=None):
        if player is not None and player.current_room != self.current_room and not self.in_inv:
            display("You don't see any "+self.name+" here.")
        else:
            display("You see "+object_list_text([self])+". "+self.descr())

    def descr(self):
        return "There is nothing special about this "+self.name+"."

    def open(self, player=None):
        display("You can't open that!")

    def close(self, player=None):
        display("You can't close that!")

    def pickup(self, player):
        if player.current_room != self.current_room:
            display("You don't see any "+self.name+" here.")
            return

        if self.is_portable:
            player.inventory.append(self)
            display("You pick up the "+self.name+".")
            try:
                self.current_room.objects.remove(self)
            except ValueError:
                pass
            self.current_room = None
            self.in_inv = True 
        else:
            display("You can't pick that up!")

    def drop(self, player):
        try:
            player.inventory.remove(self)
            player.current_room.place_object(self)
            self.in_inv = False
        except ValueError:
            display("You weren't carrying that!")
        
class Monster(object):
    def __init__(self):
        self.is_dead = False
        self.is_trapped = False
        self.is_hiding = False
        self.is_attacking = False
        self.current_room = None

    # TODO
        # if it's in the bathroom or kitchen, hide in the closet
        # if it's in the living room or foyer, hide in the attic
        # if it's in the bedroom, pick one

        # if it's already hiding, return false
    def hide(self):
        if self.is_hiding:
            return False
        self.hiding = True
        return True

    def is_nearby(self, player):
        if player is not None and self.current_room in player.current_room.exits.values():
            return True
        return False
    
