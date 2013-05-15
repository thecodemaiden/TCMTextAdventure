from game_library import Room, Item
from game_constants import *

# the candle is a very special object
class Candle(Item):
    def __init__(self, name=OBJ_CANDLE):
        super (Candle, self).__init__(name)
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
        lighter = [x for x in others if x.name == OBJ_LIGHTER]
        if len(lighter) > 0:
            if self.lit:
                display("The candle is already lit!")
            else:
                display("You use the lighter to light the candle.")
                self.lit = True
        else:
                display("What can you light the candle with?")

    def descr(self):
        if self.lit:
            return "The candle is lit."
        else:
            return "The candle is not lit."


candle = Candle()

# the spray can has only 3 uses
class SprayCan(Item):
    def __init__(self, name=OBJ_WD40):
        super (SprayCan, self).__init__(name)
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

key = Item(OBJ_KEY)

note = Item(OBJ_NOTE)
note.description = "The note says 'YZZYX'"

dresser = Item(OBJ_DRESSER)
dresser.is_portable = False
dresser.contents.append(note)
dresser.is_open = False

grindstone = Item(OBJ_GRINDSTONE)
grindstone.is_portable = False

lighter = Item(OBJ_LIGHTER)
cleaver = Item(OBJ_CLEAVER)

#the window depends on where it is!
class Window(Item):
    def __init__(self, name=OBJ_WINDOW):
        super(Window, self).__init__(name)
        self.is_portable = False

    def describe(self):
        display("You see a window. "+self.descr())

    def descr(self):
        word = "open"
        if not self.is_open:
            word = "closed"

        return "The window is "+word+"."

    def open(self, player=None):
        if self.current_room.name == RM_LIVING:
            self.is_open = True
            display("The window comes open, with some effort.")
        else:
            display("You nearly strain yourself trying to open the window, but it seems sealed shut.")
    
        
# set up the map! i was tempted to make some impossible topology... but why hurt myself?

kitchen = Room(RM_KITCHEN)
bathroom = Room(RM_BATH)
bedroom = Room(RM_BED)
closet = Room(RM_CLOSET)
attic = Room(RM_ATTIC)
foyer = Room(RM_FOYER)
living_room = Room(RM_LIVING)

living_room.exits = {DIR_SOUTH: kitchen, DIR_EAST: foyer}

kitchen.exits = {DIR_NORTH: living_room, DIR_EAST: bathroom}

bathroom.exits = {DIR_WEST: kitchen, DIR_NORTH: closet, DIR_EAST: bedroom}

closet.exits = {DIR_SOUTH: bathroom}

bedroom.exits = {DIR_WEST: bathroom, DIR_NORTH: foyer}

foyer.exits = {DIR_WEST: living_room, DIR_SOUTH: bedroom, DIR_UP: attic}
foyer.place_object(dresser)

attic.exits = {DIR_DOWN: foyer}


# now for the windows
windows = []
right_window = None

for room in [kitchen, bathroom, bedroom, closet, attic, foyer, living_room]:
    w = Window()
    room.place_object(w)
    if room.name == RM_LIVING:
        main_window = w
