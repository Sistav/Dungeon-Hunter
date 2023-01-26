# Program   : Dungeon Hunter
# Programmer: Georgios Dialynas-Vatsis and Iftakher Hossain
# Date      : May 24, 2021
# Description: Command line dungeon crawler for the computer science project

# Importing the libraries necessary for the program
import sys
import os
import time
import random
import threading


# Setting enviorment variables to be changed later on 
pygame_import = False
compatibility_mode = False

# Try importing the microsoft visual c library; if we can't then we set compatibility_mode on
try:
    import msvcrt
except:
    compatibility_mode = True

# Music variables
mixer = "I can set this to whatever because we set it to something else later"
which_folder = 1
song_cont = False
music_on = True

# game variables
amount_of_enemies = 0
player_level = 1
enemy_level = 0
current_enemy_name = ""
player_dead = False
player_health = 100
score = 0
total_score = 0
enemy_health = 0

# Game Array-like variables
items_dictionary = {"Stick":0,"Apple Pie":0,"Brick":0,"Strength Potion":0}
folders = ["Game","Menu","Death"]

def music():
    global which_folder
    global song_cont
    global mixer
    global folders
    global music_on
    
    old_which_folder = 1
    while music_on:
        # set this to make sure the music doesn't change
        old_which_folder = which_folder
        
        # Get all songs in the selected folder
        _, _, filenames = next(os.walk(f"Game Music\{folders[which_folder]}"))
        # pick a random song from said folder
        song = f"Game Music\{folders[which_folder]}\{random.choice(filenames)}"

        # Create the sound item from the song path
        sound = pygame.mixer.Sound(song)
        # Load the song and set it's volume to 0
        mixer.music.load(song)
        mixer.music.set_volume(0)
        # Play it
        mixer.music.play()
        
        # Set a counter to count the seconds
        counter = 0
        # get the length of the song so we know when to play another one
        song_length = int(mixer.Sound.get_length(sound)) 
        song_cont = True
        
        while counter <= song_length and song_cont and music_on:
            # If given new instructions to change songs, stop the loop and queue a new song
            if old_which_folder != which_folder or not song_cont:
                # stops the music 
                song_cont = False
                mixer.music.stop()
            else:
                # adds 1 second to the time counter
                counter += 1
                # fade in the music
                if counter <= 10:
                    mixer.music.set_volume(.05 * counter)
                # fade out the music
                elif song_length - counter <= 10:
                    mixer.music.set_volume(.05 * (song_length - counter))
                time.sleep(1)

def change_music(current_song_type):
    global song_cont
    global which_folder
    # check to make sure that we're changing the type of music
    # if we didn't do this the music would change every few seconds
    if current_song_type != which_folder:
        song_cont = False
        which_folder = current_song_type
        wait_for_music()

def wait_for_music():
    global song_cont
    global pygame_import
    if pygame_import and not compatibility_mode:
        # If we can use sound, we delay the game till we can guarantee it's playing
        while song_cont == False:
            print("Loading")
            time.sleep(1)

def check_compatibility():
    global compatibility_mode
    global pygame_import
    # check if the platform is compatible or the game is being run in idle 
    if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin" or 'idlelib.run' in sys.modules or compatibility_mode:
        compatibility_mode = True
        pygame_import = False
        # Let the user know what's going on 
        print("Your computer isn’t fully compatible with the game. To run Dungeon Hunter at its best, make sure to run the game in CMD on windows.")
    else:
        # if everything works, then we're good to go
        compatibility_mode = False

def selection(choices = ["Yes","No"]):
    # Default selection menu, if nothing is specified it sticks to yes and no for ease of use
    # this is done for cosmetic purposes 
    print()

    # if a non compatible computer is used, we use a simple input method using the number keys and enter
    if compatibility_mode:
        for i in range(len(choices)):
            # prints out all the choices
            print(f"{i+1}) {choices[i]}")
        choice = input()
        # Verification to make sure it's a valid choice
        if choice.isdigit() and int(choice) <= len(choices) and int(choice) >= 1:
                 returned_var = int(choice)
        else:
            returned_var =  selection(choices)
        print()
        return returned_var

    else:
        # sets default choice to the first option
        choice = 0
        # renders that choice
        render_choices(choice,choices)
        # grab input to start the loop
        keyin = msvcrt.getch()

        # check if the user pressed enter
        while keyin != b'\r':
            # if choice is up or right and we can move in that direction
            if keyin == b'w' or keyin == b'a' or keyin == b'W' or keyin == b'A':
                if choice > 0:
                    choice -= 1
                    render_choices(choice,choices)
            # if choice is down or left and if we can move in that direction
            elif keyin == b's' or keyin == b'd' or keyin == b'S' or keyin == b'D':
                if choice <= len(choices)-2:
                    choice += 1
                    render_choices(choice,choices)
            # grab the users input to see what they want to do for the next iteration
            keyin = msvcrt.getch()

        # once we get said choice and are out of the loop we can clear the console using this command
        print(" "* (len("  ".join(choices))*2))

        # returns the selected choice
        return choice + 1

def render_choices(choice,choices):
    # This renders out the menu for compatible configs
    string = ""
    for i in range(len(choices)):
        selected = False
        if choice == i:
            selected = True
        # if a choice is selected it will have "><" to indicate so, if not it will have " "
        string += f" {' ' * (not selected)}{'>' * selected} {choices[i]} {'<' * selected}{' ' * (not selected)}"
    # When all is said and done print the rendered menu to console
    print(string,end='\r')

def render_map(map_array,player_location):
    # This function renders the map to the screen
    # if the user can, we clear the screen to make it more manageable
    clear_terminal()
    # Loop through the map 0,1,2,3 each represent an object and prints out their respective event-type
    # Take that event and add it to the string and print out the string
    for y in range(len(map_array)):
        line = ""
        for x in range(len(map_array[y])):
            if map_array[y][x] == 0:
                line += "   "
            if [x,y] == player_location:
                line += "[P]"
            elif map_array[y][x] == 1:
                line += "[ ]"
            elif map_array[y][x] == 2:
                line += "[?]"
            elif map_array[y][x] == 3:
                line += "[E]"
        print(line)

def create_map(size=5):
    # create an empty array to save the details of the map
    map_array = []
    # use the size parameter to make the map a square with size x size area
    for i in range(size):
        map_array.append([])
        for _ in range(size):
            # Chance to blank represents the denominator in a 1/x
            # for each block that spawns that fraction is its chance to not be a usable tile
            chance_to_blank = 2
            # add it to the map array
            map_array[i].append(int(random.randint(0,chance_to_blank) != 0))
        # Make the top left corner of the map (the spawn point) a normal space 
        # so that the player isn't assualted when they spawn
        map_array[0][0] = 1
    # send this over to the fucntion that checks if the map is useable
    return map_check(map_array,size)         

def map_check(map_array,size):
    # We create a list of tuples of that we know are good points
    # We add the only point that we know is good which is the starting position... (1,1)
    # by good I mean able to walk on, or usable  
    checked_pos = [(0,0)]
    # We check over the amount of times the array is wide just to fix a small issue with the algorithm
    for _ in range(size): 
        # for each item in the map array
        for y in range(len(map_array)):
            for x in range(len(map_array[y])):
                # skip over the starting point because we know it's good
                # The algorithm works by checking to see if each point is connected to a previously known "good point"
                # if it is connected and its a usable point then we add it to the checked_pos array which has all "good points"
                if (x,y) != (0,0):
                    # check right 
                    if x + 1 < len(map_array[y]):
                        if (x,y) not in checked_pos:
                            if map_array[y][x+1] != 0 and (x+1,y) in checked_pos:
                                checked_pos.append((x,y))
                            # check down
                            if (y + 1) < len(map_array):
                                if map_array[y+1][x] != 0 and (x,y+1) in checked_pos:
                                    checked_pos.append((x,y))
                            # check left
                            if x - 1 >= 0:
                                if map_array[y][x-1] != 0 and  (x-1,y) in checked_pos:
                                    checked_pos.append((x,y))
                            # check up
                            if y - 1 >= 0:
                                if map_array[y-1][x] != 0 and (x,y-1) in checked_pos:
                                    checked_pos.append((x,y))
    
    # if we don't have at least 2 rows worth of usable space, we make a new map
    if len(checked_pos) < (size * 2):
        returned_map = create_map(size)

    else:
        # This function takes all points that aren't "good" and deletes them from the map
        for y in range(len(map_array)):
            for x in range(len(map_array[y])):
                if not (x,y) in checked_pos:
                    map_array[y][x] = 0
        returned_map = add_map_features(map_array)

    # return the finished map for further processing
    return returned_map

def add_map_features(map_array):
    global amount_of_enemies
    # save a copy of the old map just in case
    old_map_array = map_array
    check = True

    while check:
        amount_of_enemies = 0
        map_array = old_map_array
        # For each item in the map
        for y in range(len(map_array)):
            for x in range(len(map_array[y])):
                # if the point is good and isn't the starting point
                if map_array[y][x] != 0 and ((x,y) != (0,0)):
                    # set the point to either an event, a enemy or a blank good point
                    if random.randint(1,3) == 1:
                        map_array[y][x] = random.randint(2,3)
                        # if we do add an enemy we're good to go because we only need 1 enemy for the game to function
                        if map_array[y][x] == 3:
                            amount_of_enemies += 1
                            check = False
                    else:
                        map_array[y][x] = 1
    # send this back to the gameloop
    return map_array

def move_player(map,player_location):
    if compatibility_mode:
        # forward to our selection function, which already checks for errors so we don't have to
        choice = selection(["Up","Down","Left","Right"])
        # if they want to go up and they can go up we move 'em up
        if choice == 1:
            if player_location[1] > 0 and map[player_location[1]-1][player_location[0]] != 0:
                player_location[1] -= 1
        # Same for down
        elif choice == 2:
            if player_location[1] + 1 < len(map) and map[player_location[1]+1][player_location[0]] != 0:
                player_location[1] += 1
        # same for left
        elif choice == 3:
            if player_location[0] > 0 and map[player_location[1]][player_location[0]-1] != 0:
                player_location[0] -= 1
        # same for right
        elif choice == 4:
            if player_location[0] + 1 < len(map) and map[player_location[1]][player_location[0]+1] != 0:
                player_location[0] += 1
    
    else:
        loop_bool = True
        while loop_bool:
            # get the user's input
            keyin = msvcrt.getch()
            # the code is almost identical to the one above except we have error checking in the form of a while loop
            # If the player moves then we stop the loop and return their location
            if keyin == b'w' or keyin == b'W':
                if player_location[1] > 0 and map[player_location[1]-1][player_location[0]] != 0:
                    player_location[1] -= 1
                    loop_bool = False
            elif keyin == b'a' or keyin == b'A':
                if player_location[0] > 0 and map[player_location[1]][player_location[0]-1] != 0:
                    player_location[0] -= 1
                    loop_bool = False
            elif keyin == b's' or keyin == b'S':
                if player_location[1] + 1 < len(map) and map[player_location[1]+1][player_location[0]] != 0:
                    player_location[1] += 1
                    loop_bool = False
            elif keyin == b'd' or keyin == b'D':
                if player_location[0] + 1 < len(map) and map[player_location[1]][player_location[0]+1] != 0:
                    player_location[0] += 1
                    loop_bool = False
    return player_location

def is_player_on_event(map,player_location):
    # This function just returns the event that the player is on
    return map[player_location[1]][player_location[0]]

def clear_tile(map,player_location):
    # This function clears the tile back to a blank "Good tile"
    # and if there was an enemy on the tile it reduces the amount of enemies by 1
    global amount_of_enemies
    if map[player_location[1]][player_location[0]] == 3: 
        amount_of_enemies -= 1
    map[player_location[1]][player_location[0]] = 1
    return map

def generate_enemy(enemy_in_a_room,point):
    enemy_prefix = ["Cave","Venom","Gut","Infernal","Frost","Cinder","Night","Murk","Spectral","Spirit","Smog","Inferno","Soul","Tainted","Death"]
    enemy_suffix = ["body","snare","pod","serpent","ling","hound","paw","fiend","flayer","hand","sword","crackle","wing"]
    # If we can't find an existing name of an enemy for that tile
    # we add one, we check this using tuples in a dictionary called enemy_in_a_room
    point = (point[1],point[0])
    if not point in enemy_in_a_room:
        # generate a random name from the lists
        enemy_in_a_room[point] = random.choice(enemy_prefix) + random.choice(enemy_suffix)
    # then we return the given or checked enemy name
    returned_name = enemy_in_a_room[point]
    return returned_name

def add_score(multiplier = 1):
    global score
    global total_score
    global player_level
    # This is the level up system
    base = 50 * multiplier
    added = random.randint(base//4,base)
    # We generate a random number and add it to the players xp
    score += added
    # since score caps at 100, we need total score for the leaderboards later on
    total_score += added
    time.sleep(1)
    print(f"You gained {added} XP\n")
    if score >= 100:
        # if the users score caps out we subtract 100 and give em a level
        score -= 100
        # levels increase damage out
        player_level += 1    
        time.sleep(1)
        print(f"You Leveled up to level {player_level}\n")
    time.sleep(1)

def fight(current_enemy_name):
    # This is the combat loop
    global compatibility_mode
    global player_dead
    global player_health
    global enemy_level
    global enemy_health
    # We generate a random amount of health dependant on the enemies level
    enemy_health = generate_enemy_health(enemy_level)
    
    clear_terminal()

    print(f"You encountered a {current_enemy_name}\n")

    # Start the loop
    loop_bool = True
    while loop_bool:

        time.sleep(1)
        print("What do you do?")
        # Poll the user's choice
        choice = selection(["Attack","Items","Stats","Flee"])
        clear_terminal()

        if choice == 1:
            # Get a random amount of damage dependant on the players level
            damage = player_attack()
            enemy_health -= damage
            time.sleep(1)
            print(f"You did {damage} damage to the {current_enemy_name}\n")
            time.sleep(1)

            # if the player kills the enemy
            if enemy_health <= 0:
                print(f"You killed the {current_enemy_name}\n")
                # gain xp
                add_score()
                # exit the loop
                killed = True
                loop_bool = False
            else:
                # If the enemy doesn't die, we let them take their turn
                # We generate a random number for the enemy dependant on their level
                enemy_damage = enemy_attack(enemy_level)
                player_health -= enemy_damage
                print(f"The {current_enemy_name} did {enemy_damage} damage to you\n")

            # if the player dies we exit the loop
            if player_health <= 0:
                player_dead = True
                loop_bool = False
                killed = False

        # if the user decides to check their items
        elif choice == 2:
            check_items()
            # if they kill the enemy, we exit the loop
            if enemy_health <= 0:
                print(f"You killed the {current_enemy_name}\n")
                add_score()
                # exit loop
                killed = True
                loop_bool = False
        
        elif choice == 3:
            # Displays stats, and clears screen after input
            print(f"Player Health:\t{player_health}\nEnemy Health:\t{enemy_health}")
            print(f"Player Level:\t{player_level}\nEnemy Level:\t{enemy_level}")
            input("Press enter to return to battle")
            clear_terminal()

        elif choice == 4:
            # Exit the loop without anything else
            killed = False
            loop_bool = False
            print("You fled, you coward!")
            time.sleep(2)
    return killed

def generate_enemy_health(enemy_level):
    enemy_health_multiplier = 25
    max_enemy_health = enemy_level * enemy_health_multiplier
    # we generate an amount of health from a random number from half of the max to the max,
    # if the max is 25, we would pick a number from 12 to 25.
    return random.randint(max_enemy_health//2,max_enemy_health)

def player_attack():
    global player_level
    # We generate the player attack based on 3 factors, 2 of which are displayed, the last is the players level
    player_attack_base_damage = 10
    player_attack_multiplier = 3

    max_player_attack = player_attack_base_damage + (player_attack_multiplier * player_level)
    # It picks a random number from 1/3rd of the max to the max
    return random.randint(max_player_attack//3,max_player_attack)
    
def enemy_attack(enemy_level):
    # this is almost identical to the one above except we use enemy based stats
    base_enemy_damage = 5
    enemy_damage_multiplier = 3

    actual_damage = base_enemy_damage + (enemy_level * enemy_damage_multiplier)
    # picks from half of the max to the max
    return random.randint(actual_damage//2,actual_damage)

def check_items():
    global items_dictionary
    # creates 2 lists, 1 for the selection funciton, the other for the use_items() function
    selection_list = []
    index = []
    # Set this for later
    any_items = False
    # Go through all the items and add them to the list for the selection
    for a,b in items_dictionary.items():
        if b >= 1:
            selection_list.append(f"{a}: {b}")
            index.append(a)
            # If we have at least 1 item, we can set any_items to true
            any_items = True
    # If the user has no items we can stop here
    if any_items == False:
        print("You have no items\n")
        time.sleep(2)
        clear_terminal()
    # If they do have items, we add a close option to them and pass it through to selection
    else:
        selection_list.append(f"Close") 
        choice = selection(selection_list)
        # if the user doesn't choose close we can forward it to the selection function
        if choice != len(selection_list):
            # Pass through the string of the chosen item
            use_items(index[choice-1])

def use_items(item_type):
    global enemy_health
    global current_enemy_name
    global player_health
    global items_dictionary
    if item_type == "Stick":
        print(f"You toss the stick at the {current_enemy_name}\n")
        time.sleep(1)
        # picks a number between 1 and 5 and does that damage to the enemy
        damage_of_stick = random.randint(1,5)
        enemy_health -= damage_of_stick
        print(f"It did {damage_of_stick} damage")

    elif item_type == "Apple Pie":
        print("You ate the apple pie you were saving for later\n")
        time.sleep(1)
        # Heals the user 20 hp
        apple_increase = 20
        player_health += apple_increase
        print(f"You gained {apple_increase} HP")

    elif item_type == "Brick":
        print(f"You Whip the Brick at the {current_enemy_name}\n")
        # does 20 damage to the user 
        damage_of_brick = 20
        enemy_health -= damage_of_brick
        print(f"It did {damage_of_brick} damage")

    elif item_type == "Strength Potion":
        print("You feel fantastic")
        time.sleep(1)
        add_score(2)
        # if the user selects this, we give the user xp
    # Remove the item from the users inventory
    items_dictionary[item_type] -= 1

    time.sleep(1)
    print()
    clear_terminal()

def gameloop():
    # This is where the magic happens, this is basically our main() of the game, it calls upon other functions to create the game
    global player_dead
    global amount_of_enemies
    global current_enemy_name
    global enemy_level
    global player_health
    size_of_map = 5
    print("Loading")
    time.sleep(2)
    # pretty self explanitory
    while not player_dead:
        change_music(0)
        # if there are no enemies left of screen we make a new map
        if amount_of_enemies <= 0:
            if enemy_level != 0:
                clear_terminal()
                print("You go up a floor")
                time.sleep(1)
            enemy_level += 1
            map = create_map(size_of_map + enemy_level)
            player_location = [0,0]
            enemy_in_a_room = {}
        else:
            # If there are still enemies, we render out the map and have the player move
            render_map(map,player_location)
            player_location = move_player(map,player_location)
        # we then check for the current event the player is standing on
        event = is_player_on_event(map,player_location)
        if event == 2:
            current_event = event_picker()
            actual_events(current_event)
            clear_tile(map,player_location)
        # Enemy fight sequence
        elif event == 3:
            # generate the enemies name and then fight em
            current_enemy_name = generate_enemy(enemy_in_a_room,player_location)
            # pass that name to the fight function and if they kill it, clear the tile
            if fight(current_enemy_name):
                clear_tile(map,player_location)
                clear_terminal()
        if player_health <= 0:
            player_dead = True
    # also super duper self explanitory
    if player_dead:
        death_and_highscores()

def credits():
    string = "Made By Georgios Dialynas-Vatsis and Iftakher Hossain"
    # we iterate through half of the string because we render the string at both ends
    if not compatibility_mode:
        for i in range(1,len(string)//2 +1):
            # the first part renders from the beggining to i, the last part renders from -i to the end, 
            # and the middle part fills in the space
            print(f"{string[:i]}{' ' * (len(string) - (i*2))} {string[-i:]}",end='\r')
            # delay for visual effect
            time.sleep(.1)
        # print the full thing to keep it on the screen
    print(string+ "    ")
    print("Music provided by opengameart.org")
    time.sleep(2)
    menu()

def clear_terminal():
    global compatibility_mode
    # if compatible it clears the terminal
    if not compatibility_mode:
        os.system("cls")

def actual_events(which_event):
    clear_terminal()
    global player_health
    global items_dictionary
    # Takes the randomly generated number and picks a function using that number

    if which_event == 1:
        print("You stumble upon a odd looking potion.\nDo you drink it?")
        if selection() == 1:
            if random.randint(1,5) == 1:
                player_health += 20
                # gives the user a chance of 1/5 to gain 20 hp
                print("You gained 20 HP")
            else:
                print("You feel queezy")

    # Literally gives the user sticks
    elif which_event == 2:
        print("You find a bundle of sticks")
        items_dictionary["Stick"] += random.randint(2,7)

    # has a 1 in 2 chance to give the user a stick, and half a chance to lose 5 hp
    elif which_event == 3:
        print("You see a tree, with a broken branch")
        if selection(["Pull it off","Leave it Alone"]) == 1:

            if random.choice([True,False]):
                print("You pull off the branch")
                items_dictionary["Stick"] += 1

            else:
                print("You hurt your back... and lost 5 HP")
                player_health -= 5

    # Gives the user a brick
    elif which_event == 4:
        print("You stuble upon a brick")
        items_dictionary["Brick"] += 1

    # Gives the user a pie
    elif which_event == 5:
        print("You remember you packed your grandmothers apple pie")
        items_dictionary["Apple Pie"] += 1
        time.sleep(3)

    # gives the user a little bit of xp
    elif which_event == 6:
        print("You realize that you're actually a virtual character in a terminal-based python game")
        time.sleep(3)
        add_score(.5)

    # gives a 50/50 chance of getting a pie or potion
    elif which_event == 7:
        print("You encounter a chest")
        choice = selection(["Open it","Leave it alone"])
        if choice == 1:
            if random.choice([True,False]):
                items_dictionary["Apple Pie"] += 1
                print("You got a pie")
            else:
                items_dictionary["Strength Potion"] += 1
                print("You find a Potion of Strength")

    # Gives the user a potion if they choose wisely
    elif which_event == 8:
        print("You encounter a mysterious stranger")
        choice = selection(["Say Hello","Book it"])

        if choice == 1:
            items_dictionary["Strength Potion"] += 1
            print("The mysterious stranger gave you a potion of strength")
    time.sleep(2)

def event_picker():
    # Generate a random event and pass it back
    amount_of_events = 8
    return random.randint(1,amount_of_events)

def menu():
    # This is the main menu and doesn't really need that much commenting
    global compatibility_mode

    clear_terminal() 
    print("\nWelcome to Dungeon Hunter")
    choice = selection(["Start Game","How to play","Credits"])
    # if the user picks start game... we start the game
    if choice == 1:
        gameloop()
    elif choice == 2:
        # Prints tutorial
        if compatibility_mode:
            print("Use the number keys to make a selection, then press enter to confirm.\n")
            input("Press Enter To Continue\n")
            print("Go around the dungeon slaying enemies, beat all enemies on a level to go to the next\n")
            input("Press Enter To Continue\n")
            print("Enemies are marked by 'E', Random encounters are marked with a '?', and the player is marked with a 'P'\n")
            input("Press Enter To Continue\n")
            menu()
        else:
            print("Use WASD to make a selection, then press enter to confirm.\n")
            input("Press Enter To Continue\n")
            print("Go around the dungeon slaying enemies, beat all enemies on a level to go to the next\n")
            input("Press Enter To Continue\n")
            print("Enemies are marked by 'E', Random encounters are marked with a '?', and the player is marked with a 'P'\n")
            input("Press Enter To Continue\n")
            menu()
    elif choice == 3:
        # prints the credits
        credits()

def death_and_highscores():
    # If you've read up to here I am SO, SO, SO SORRY Mr. Fong but if you've noticed 
    # this functions name is a play on Ben Franklin's "death and taxes" quote
    global total_score
    global music_on

    # set the music to the death theme
    change_music(2)
    clear_terminal()

    print("\nYou Died\n")
    print(f"Score: {total_score}\n")

    # Confirm that the user's name is 3 digits and also only letters from the alphabet
    loop_bool = True
    while loop_bool:
        name = input("Enter Your name\n")
        # checks if alpha and isnt we loop again
        if not name.isalpha():
            clear_terminal()
            print("Your name contains non-letter symbols\n")
        # checks if the user entered a name more than 3 letters
        elif len(name) > 3:
            clear_terminal()
            print("Your name is more than 3 letters\n")
        else:
            loop_bool = False
    
    # set the file name 
    file_name = 'highscores.txt'

    # open the file
    appended_file= open(file_name, 'a+')

    # Add the users name and score
    appended_file.write(name + "\n")
    appended_file.write(str(total_score) + "\n")

    # close the file
    appended_file.close()

    # reopen the file in read mode
    read_file= open(file_name, 'r')

    # create blank arrays
    highscores = []
    names = []

    # Create these two to get into the loop
    line_read_a = " "
    line_read_b = " "

    while line_read_a != "" and line_read_b != "":
        # Read the lines and strip the newline character
        line_read_a = read_file.readline().strip("\n")
        line_read_b = read_file.readline().strip("\n")

        # only append them if the second line is an actual number
        if line_read_b.isdigit():
            highscores.append(int(line_read_b))
            names.append(line_read_a)
    # close the file
    read_file.close()

    # sort the highscores in the order of highest to lowest
    for i in range(len(highscores)):
        for j in range(i + 1, len(highscores)):
            if(highscores[i] < highscores[j]):
                # temp is used to swap the scores
                temp = highscores[i]
                highscores[i] = highscores[j]
                highscores[j] = temp

                temp = names[i]
                names[i] = names[j]
                names[j] = temp

    print("\nHIGHSCORES")
    # print the names
    for i in range(len(highscores)):
        if names[i] != "" and highscores[i] != "":
            print(f"{names[i].upper()}:\t{highscores[i]}")
    print("Thanks for playing")
    music_on = False
    time.sleep(3)
    exit()

check_compatibility()

# The reason we're running in the main part of the code and not in a function is because it's difficult to import libraries in functions,
# So it makes more sense to just do it here
try:
    if not compatibility_mode:
        # Stops the "welcome to pygame message"
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
        # check if we can even import pygame
        import pygame

        # Start the audio mixer
        mixer = pygame.mixer
        mixer.init()

        # Start a new thread running the music function
        thread = threading.Thread(target = music)
        thread.start()
        
        # We can now rest assured that Pygame is installed
        pygame_import = True
except:
    # if we can't get pygame working, we let the user know
    print("Please install Pygame for the full expeirence")
    time.sleep(1)

# Wait for the music to kick in before starting the menu
wait_for_music()
menu()