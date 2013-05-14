from game_library import Player, Monster, Room, Item
from game_setup import kitchen, bathroom, bedroom, closet, attic, foyer, living_room
from game_constants import *
from game_parser import *


def do_parse(cmd):
	line_parser = ParserFSM()
	for word in cmd.split():
		line_parser.consume(word)
	return line_parser.output
	

monster = Monster()
monster.current_room = attic

player = Player()
player.current_room = foyer
player.current_room.onEntered(player, monster)

done = False

command = ""
while not done:
    command = raw_input("> ")
    next_action = do_parse(command)
    if windows_open:
        gas_conc *= 0.8
    print next_action
    done = (command.lower() == "quit" or command.lower() == "q" or player.is_dead or player.is_escaped)

if player.is_dead:
	display("You have died!")
elif player.is_escaped:
	display("You have escaped!")
else:
	print "Quitter!"
