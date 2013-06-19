from game_library import Player, Monster, Room, Item
from game_setup import kitchen, bathroom, bedroom, closet, attic, foyer, living_room
from game_setup import candle, can_VC60, key, note, dresser, grindstone, lighter, cleaver, windows, main_window, object_map
from game_constants import *
from game_parser import *
from random import randrange

# TODO: get rid of all the passing around of monster, somehow

def do_parse(cmd):
	line_parser = ParserFSM()
	for word in cmd.split():
		line_parser.consume(word)
	return line_parser.output
	

monster = Monster()
monster.current_room = attic
monster.burnt_turns = 3

object_map[PARSE_MONSTER] = monster

player = Player()
player.enter(foyer, monster)

done = False

command = ""

def move(dir):
    if dir in compass_directions and not player.has_compass():
        display("I don't know which way that is.")
        return False
    else:
        dir = player_to_compass(dir, player.facing)
        if dir in player.current_room.exits:
            new_room = player.current_room.exits[dir]
            player.facing = dir
            player.enter(new_room, monster)
            return True
        else:
            display("You can't go that way!")
            return False

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
            return False
        else:
            dir = player_to_compass(dir, player.facing)
            to_show = player.current_room.get_exit_descr(dir, not player.has_compass(), player.facing)
            if to_show is None:
                display("There is nothing over there.")
            else:
                display(to_show)
    return True   

def turn(dir):
    if dir in compass_directions and not player.has_compass():
        display("I don't know which way that is.")
        return False
    else:
        dir = player_to_compass(dir, player.facing)
        if dir == DIR_UP or dir == DIR_DOWN:
            look(dir)
        else:
            player.facing = dir 
            display(player.current_room.list_exits(not player.has_compass(), player.facing, player.found_trapdoor))
        return True

def items_do_all(items, method, error_format='What {0}?'):
    success_count = 0
    for x in items:
        try:
            if x == OBJ_WINDOW:
                windows = [x for x in player.current_room.objects if x.name == OBJ_WINDOW]
                item = windows[0] 
            else:
                item = object_map[x]
            getattr(item, method)(player)
            success_count+=1
        except KeyError, ValueError:
            display(error_format.format(x))
        except AttributeError:
            display("You can't do that to the "+x+".")
    return success_count > 0

def descr_all(items):
    subj = None
    if len(items) > 0:
        subj = items[0]
    if subj in object_names or subj == PARSE_MONSTER:
        return items_do_all(items, "describe")
    else:
        return look(subj)
    
def use_items(items):
    # here we check for combos: lighter + spray, cleaver + grindstone, cleaver + dresser
    # if monster is in the room, use cleaver will chop him
    try:
       item_objs = [object_map[i] for i in items]
    except KeyError:
        display ("... What?")
        return False
    else:
        if gas_conc >= 1.6:
            # BOOM?
            if OBJ_LIGHTER in items:
                player.die_now("As you click the lighter on, you hear a loud whooshing, and the room erupts in flame.")
        
        return True

def do_tick():
    # on every action
    global gas_conc
    global main_window
    old_conc = gas_conc
    if main_window.is_open and oven.is_on:
        # window is open & oven is on OR window is closed and oven is off
        pass
    elif main_window.is_open and not oven.is_on:
        gas_conc *= 0.8
    elif not main_window.is_open and oven.is_on:
        gas_conc *= 1.005
    if (old_conc < 1.5 and gas_conc >= 1.5) or (old_conc >= 1.5 and gas_conc < 1.5):
        look(ENV_SMELL)

    # also, explode if the gas conc is high and the candle is lit
    if (candle.lit and gas_conc >= 1.6):
        candle_room = 
    # monster hides from lit candle
    hide_monster = False
    can_see_monster = monster.current_room == player.current_room
    if candle.lit:
        if (candle.in_inv or candle.current_room == player.current_room) and can_see_monster:
            display("The monster shrieks and recoils from the light.")
            hide_monster = True
        elif candle.current_room == monster.current_room:
            display("You hear a bloodcurdling shriek, and hear muffled, clawed footsteps.")
            hide_monster = True

    available_rooms = monster.current_room.exits.values()
    try:
        if candle.lit: 
            available_rooms.remove(candle.current_room)
            if candle.in_inv:
                available_rooms.remove(player.current_room)
    except ValueError:
        pass # the candle may be in room 'None'

    idx = randrange(len(available_rooms))
    new_room = available_rooms[idx]

    if hide_monster:
        monster.just_moved = False #FLEE! No matter what!
        if can_see_monster:
            display("It flees into the "+new_room.name+".")
        monster.move_to(new_room)
    elif monster.burnt_turns > 0:
        monster.is_attacking = False
        monster.burnt_turns -= 1
    elif can_see_monster:
        if not monster.is_attacking and not monster.just_moved:
            monster.is_attacking = True
            display("The monster bares its teeth and raises its front claws. Do something!")
        else:
            player.die_now("The monster springs on you, pinning you down with its claws. The last thing you see is its maw gaping open...")
    elif player.current_room in available_rooms:
        monster.move_to(player.current_room)
        if monster.current_room == player.current_room:
            display("A monster leaps into the room, snarling.")
    else:
        # the monster doesn't do path finding
        monster.move_to(new_room)
        if monster.is_nearby(player):
            display("You hear a scratching sound.")

        
           
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
        tick = False
    else:
        verb = next_action[PARSE_ACTION]
        if verb == ACTION_INVENTORY:
            display("You have: " + object_list_text(player.inventory))
            tick = False
        elif verb == ACTION_WAIT:
            pass
        elif verb == ACTION_MOVE:
            tick = move(next_action[PARSE_SUBJECTS][0])
        elif verb == ACTION_TURN:
            tick = turn(next_action[PARSE_SUBJECTS][0])
        elif verb == ACTION_EXAMINE:
            tick = False
            tick = descr_all(next_action[PARSE_SUBJECTS])
        elif verb == ACTION_TAKE or verb == ACTION_DROP or verb == ACTION_OPEN or verb == ACTION_CLOSE:
            tick = items_do_all(next_action[PARSE_SUBJECTS], verb)
        elif verb == ACTION_USE:
           tick = use_items(next_action[PARSE_SUBJECTS]) 
        else:
            print next_action

        if tick:
            do_tick()

    if not player.is_dead and gas_conc > 2.0:
        player.die_now("The stench of propane is overwhelming. Your vision spins, and you fall to the ground, gasping for air.")

    if player.is_dead or player.is_escaped:
        break


if player.is_dead:
	display("You have died!")
elif player.is_escaped:
	display("You have escaped!")
else:
	display("Goodbye...")
