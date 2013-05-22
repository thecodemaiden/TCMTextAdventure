from game_library import Player, Monster, Room, Item
from game_setup import kitchen, bathroom, bedroom, closet, attic, foyer, living_room
from game_setup import candle, can_VC60, key, note, dresser, grindstone, lighter, cleaver, windows, right_window, object_map
from game_constants import *
from game_parser import *

# TODO: get rid of all the passing around of monster, somehow

def do_parse(cmd):
	line_parser = ParserFSM()
	for word in cmd.split():
		line_parser.consume(word)
	return line_parser.output
	

monster = Monster()
monster.current_room = attic

object_map[PARSE_MONSTER] = monster

player = Player()
player.enter(foyer, monster)

done = False

command = ""

def move(dir):
    if dir in compass_directions and not player.has_compass():
        display("I don't know which way that is.")
    else:
        dir = player_to_compass(dir, player.facing)
        if dir in player.current_room.exits:
            new_room = player.current_room.exits[dir]
            player.facing = dir
            player.enter(new_room, monster)
        else:
            display("You can't go that way!")

def look(dir):
    if dir == DIR_UP:
        dir = ENV_ABOVE
    if dir == DIR_DOWN:
        dir = ENV_BELOW

    if dir is None:
        player.current_room.onEntered(player, monster)
    elif dir in env_properties:
        display(player.current_room.get_description(dir, player, monster))
    else:
        if dir in compass_directions and not player.has_compass():
            display("I don't know which way that is.")
        else:
            dir = player_to_compass(dir, player.facing)
            to_show = player.current_room.get_exit_descr(dir, not player.has_compass(), player.facing)
            if to_show is None:
                display("There is nothing over there.")
            else:
                display(to_show)
        

def turn(dir):
    if dir in compass_directions and not player.has_compass():
        display("I don't know which way that is.")
    else:
        dir = player_to_compass(dir, player.facing)
        if dir == DIR_UP or dir == DIR_DOWN:
            look(dir)
        else:
            player.facing = dir 
            display(player.current_room.list_exits(not player.has_compass(), player.facing, player.found_trapdoor))

def items_do_all(items, method, error_format='What {0}?'):
    for x in items:
        try:
            item = object_map[x]
            getattr(item, method)(player)
        except KeyError:
            display(error_format.format(x))

def descr_all(items):
    subj = None
    if len(items) > 0:
        subj = items[0]
    if subj in object_names:
        items_do_all(items, "describe")
    else:
        look(subj)
    
def use_items(items):
    # here we check for combos: lighter + spray, cleaver + grindstone, cleaver + dresser
    # cleaver + monster, lighter + spray + monster
    try:
       item_objs = [object_map[i] for i in items]
    except KeyError:
        display ("... What?")
        return
    else:
        display(object_list_text(item_objs)) 

def do_tick():
    # on every action
    global gas_conc
    old_conc = gas_conc
    if windows_open:
        gas_conc *= 0.85
    else:
        gas_conc *= 1.005
    if (old_conc < 1.5 and gas_conc >= 1.5) or (old_conc >= 1.5 and gas_conc < 1.5):
        look(ENV_SMELL)


while 1:
    command = raw_input("> ")
    next_action = do_parse(command)
    
    done = next_action[PARSE_ACTION] == ACTION_QUIT

    if done:
        break

    tick = True
    action_failed = next_action[PARSE_SUBJECTS] == PARSE_ERROR
    if action_failed:
        tick = False
        if len(next_action[PARSE_SUGGEST]) > 0:
            display("I was fine up to '"+next_action[PARSE_SUGGEST]+"', but then you lost me.")
        else:
            display("I didn't quite get that. I can handle: "+", ".join(commands)+".")
    elif next_action[PARSE_ACTION] is None:
        continue # don't tick any time away unless we explicitly waited
    else:
        verb = next_action[PARSE_ACTION]
        if verb == ACTION_INVENTORY:
            display("You have: " + object_list_text(player.inventory))
        elif verb == ACTION_WAIT:
            pass
        elif verb == ACTION_MOVE:
            move(next_action[PARSE_SUBJECTS][0])
        elif verb == ACTION_TURN:
            turn(next_action[PARSE_SUBJECTS][0])
        elif verb == ACTION_EXAMINE:
            descr_all(next_action[PARSE_SUBJECTS])
        elif verb == ACTION_TAKE or verb == ACTION_DROP or verb == ACTION_OPEN or verb == ACTION_CLOSE:
            items_do_all(next_action[PARSE_SUBJECTS], verb)
        elif verb == ACTION_USE:
           use_items(next_action[PARSE_SUBJECTS]) 
        else:
            print next_action

        if tick:
            do_tick()

    if gas_conc > 2.0:
        player.die_now("The stench of propane is overwhelming. Your vision spins, and you fall to the ground, gasping for air.")

    if player.is_dead or player.is_escaped:
        break


if player.is_dead:
	display("You have died!")
elif player.is_escaped:
	display("You have escaped!")
else:
	print "Quitter!"
