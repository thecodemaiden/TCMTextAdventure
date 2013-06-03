from game_constants import *
import string

alias_dir = {"forward": DIR_FORWARD, "ahead": DIR_FORWARD, "back": DIR_BACKWARD, "behind": DIR_BACKWARD, "left": DIR_LEFT, "right": DIR_RIGHT, "up": DIR_UP, "down": DIR_DOWN, "north": DIR_NORTH, "n": DIR_NORTH, "south": DIR_SOUTH, "s": DIR_SOUTH, "east": DIR_EAST, "e": DIR_EAST, "west": DIR_WEST, "w": DIR_WEST}

alias_comm = {"leave": "drop", "move": "go", "inventory": "stuff", "i":"stuff", "get": "take", "face": "turn", "q": "quit", "inv": "stuff", "examine": "look"}

ignore_words = ["the", "to", "at", "and", "with", "a", "an"]

commands = ["wait", "look", "use", "take", "drop", "pull", "open", "close", "smell", "go", "turn", "stuff", "quit"]

# parser
PARSE_SUBJECTS = "subjects"
PARSE_ACTION = "action"
PARSE_SUGGEST = "suggestion"

PARSE_START = "start"
PARSE_DONE = "done"
PARSE_ERROR = "error"

ACTION_WAIT = "wait"
ACTION_EXAMINE = "examine"
ACTION_TAKE = "pickup"
ACTION_DROP = "drop"
ACTION_TURN = "turn"
ACTION_OPEN = "open"
ACTION_CLOSE = "close"
ACTION_MOVE = "move"
ACTION_USE = "use"
ACTION_INVENTORY = "inventory"
ACTION_QUIT = "quit"
ACTION_MAGIC = "yzzyx"

PARSE_USE_NOUN = "LOOKUP_N"
PARSE_USE_DIR = "LOOKUP_D"
PARSE_USE_ARG = "<insert>" #use whatever we resolved the word as as a subject
PARSE_UNCHANGED = "keep" # if we want to keep an action or subject the same
PARSE_IGNORE = "ignore" #eat the word and continue in the same state

PARSE_MONSTER = "monster"

PARSE_DIR = "expecting direction"
PARSE_ITEM = "expecting item"
PARSE_LOOK = "look expression"
PARSE_MOVE = "going somewhere"
PARSE_TURN = "reorienting player"
PARSE_ANY = "fallback"


# {state: {input:(output,next_state)}} 
transitions = {}
transitions[PARSE_START] = {PARSE_USE_DIR:((PARSE_USE_DIR, ACTION_MOVE), PARSE_DONE),
                            "wait":((None, ACTION_WAIT), PARSE_DONE),
                            "take":((None, ACTION_TAKE), PARSE_ITEM),
                            "drop":((None, ACTION_DROP), PARSE_ITEM),
                            "use":((None, ACTION_USE), PARSE_ITEM),
                            "look":((None, ACTION_EXAMINE), PARSE_LOOK),
                            "open":((None, ACTION_OPEN), PARSE_ITEM),
                            "close":((None, ACTION_CLOSE), PARSE_ITEM),
                            "smell":((ENV_SMELL, ACTION_EXAMINE), PARSE_DONE),
                            "go":((None, ACTION_MOVE), PARSE_MOVE),
                            "turn":((None, ACTION_TURN), PARSE_TURN),
                            "quit":((None, ACTION_QUIT), PARSE_IGNORE),
                            "stuff":((None, ACTION_INVENTORY), PARSE_DONE), 
                            "yzzyx":((None, ACTION_MAGIC), PARSE_IGNORE)
                            }

transitions[PARSE_MOVE] = {PARSE_USE_DIR:((PARSE_USE_DIR, ACTION_MOVE), PARSE_DONE)}
transitions[PARSE_LOOK] = {PARSE_USE_DIR:((PARSE_USE_DIR, ACTION_EXAMINE), PARSE_DONE),
                           PARSE_USE_NOUN:((PARSE_USE_NOUN, ACTION_EXAMINE), PARSE_ITEM)}
# make lists of items
transitions[PARSE_ITEM] = {PARSE_USE_NOUN:((PARSE_USE_NOUN, PARSE_UNCHANGED), PARSE_ITEM)}
transitions[PARSE_TURN] = {PARSE_USE_DIR:((PARSE_USE_DIR, ACTION_TURN), PARSE_DONE)}

transitions[PARSE_IGNORE] = {PARSE_ANY:((PARSE_UNCHANGED, PARSE_UNCHANGED), PARSE_IGNORE)}

#in future we will need a lexer before, to convert 2-word names into recognizable tokens

class ParserFSM(object):
    
    def __init__(self):
        self.state = PARSE_START
        self.output = {PARSE_SUBJECTS:[], PARSE_ACTION:None, PARSE_SUGGEST:""}
        self.consumed = []

    def consume(self, word):
        # clean up the word - remove punctuation
        word = word.translate(string.maketrans("",""), string.punctuation)

        if self.state == PARSE_ERROR:
            return
        next_state = self.state
        word = word.lower()
        if word not in ignore_words:
            parse_dict = transitions[self.state]
            keyword = word
            if self.state == PARSE_IGNORE:
                keyword = PARSE_ANY
            elif word in alias_dir:
                keyword = PARSE_USE_DIR
            elif word in object_names or word == PARSE_MONSTER:
                keyword = PARSE_USE_NOUN
            elif word in alias_comm:
                    keyword = alias_comm[word]
            try:
                state_info = parse_dict[keyword]
                next_state = state_info[1]
                state_subj = state_info[0][0]
                state_action = state_info[0][1]
                #print state_info
                if (state_action != PARSE_UNCHANGED):
                    self.output[PARSE_ACTION] = state_action
                if state_subj is not None and state_subj != PARSE_UNCHANGED:
                    if state_subj == PARSE_USE_DIR:
                        dir = alias_dir[word]
                        self.output[PARSE_SUBJECTS] = [dir] 
                    elif state_subj == PARSE_USE_NOUN:
                        subjs = self.output[PARSE_SUBJECTS]
                        subjs.append(word)
                    else:
                        self.output[PARSE_SUBJECTS] = [state_subj]
            except (KeyError, TypeError):
                self.state = PARSE_ERROR #straight to error state, don't do transition

        if self.state != PARSE_DONE and self.state != PARSE_ERROR:
            self.consumed.append(word)
            self.state = next_state
        else:
            # we were done but still had more to consume, or other error
            self.output[PARSE_SUGGEST] = " ".join(self.consumed)
            self.output[PARSE_SUBJECTS] = PARSE_ERROR

