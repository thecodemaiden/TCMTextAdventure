from game_library import Room, Item
from game_constants import *


# the candle is a very special object
class Candle(Item):
    def __init__(self):
        super (Candle, self).__init__()
        self.name = OBJ_CANDLE
        self.turns_left = 20
        self.lit = False

    def burn(self):
        if (self.lit):
            if (self.turns_left > 0):
                self.turns_left -= 1
            if (self.turns_left == 0):
                display("The candle burns out.")
                self.lit = False

    def use(self, player, others=[]):
        if (self.lit):
            display("You blow out the candle.")
            self.lit = False
        else:
            lighter = [x for x in others if x.name == OBJ_LIGHTER]
            if len(lighter) > 0:
                display("You use the lighter to light the candle.")
                self.lit = True
            else:
                display("What can you light the candle with?")

    def descr(self):
        if self.lit:
            return "It is lit."
        else:
            return "It is not lit."


candle = Candle()

# the spray can has only 3 uses
class SprayCan(Item):
    def __init__(self):
        super (SprayCan, self).__init__()
        self.name = OBJ_WD40
        self.uses = 3

    def descr(self):
        if self.uses > 0:
            return "There is still something left in the spray can."
        else:
            "The spray can is empty."

    def use(self, player, others=[]):
        lighter = [x for x in others if x.name == OBJ_LIGHTER]
        if self.uses > 0:
            s = "You spray a little from the can."
            if len(lighter) > 0:
                s += " The spray catches fire as it passes the lighter, and you somehow manage not to burn off your own hand."
            display(s)
        else:
            display("You press the button on the can, but there seems to be no spray left.")
 
            

can_VC60 = SprayCan()

key = Item()
key.name = OBJ_KEY

note = Item()
note.name = OBJ_NOTE
note.description = "The note says 'YZZYX'"

dresser = Item()
dresser.is_portable = False
dresser.name = OBJ_DRESSER
dresser.contents.append(note)
dresser.is_open = False

grindstone = Item()
grindstone.is_portable = False


lighter = Item()
cleaver = Item()

windows = Item()
windows.is_portable = False

# set up the map! i was tempted to make some impossible topology... but why hurt myself?

kitchen = Room()
bathroom = Room()
bedroom = Room()
closet = Room()
attic = Room()
foyer = Room()
living_room = Room()

living_room.exits = {DIR_SOUTH: kitchen, DIR_EAST: foyer}
living_room.name = "living room"

kitchen.exits = {DIR_NORTH: living_room, DIR_EAST: bathroom}
kitchen.name = "kitchen"

bathroom.exits = {DIR_WEST: kitchen, DIR_NORTH: closet, DIR_EAST: bedroom}
bathroom.name = "bathroom"

closet.exits = {DIR_SOUTH: bathroom}
closet.name = "closet"

bedroom.exits = {DIR_WEST: bathroom, DIR_NORTH: foyer}
bedroom.name = "bedroom"

foyer.exits = {DIR_WEST: living_room, DIR_SOUTH: bedroom, DIR_UP: attic}
foyer.name = "foyer"
foyer.objects.append(dresser)

attic.exits = {DIR_DOWN: foyer}
attic.name = "attic"

