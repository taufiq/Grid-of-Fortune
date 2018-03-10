import pygame
import random
import time
import aiy.audio
import aiy.cloudspeech
import aiy.voicehat

clock = pygame.time.Clock()
FPS = 60
# Colors
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

# Sizes
screen_width = 1000
screen_height = 1000

# Create screen with these specified sizes
screen = pygame.display.set_mode((screen_width, screen_height))
answer = "BANANA"
# Stores the progress of the solve
solve_state = ""
# Run through every letter in answer variable
for char in answer:
    # If there is a letter, add a space to solve_state
    if char is not " ":
        solve_state += "_"
    else:
        # If it is a space, add a space to solve_state
        solve_state += " "

# Creates a list of monies user can get from spinning
tokens = [500, 200, 400, 100, 600, 450]

# Stores the coordinates of each money token graphic text
token_coords = []
# Stores coordinates of the cursor that show which token it landed on after a spin
cursor_coords = [[], [], []]

pygame.init()
# Creates a font for drawing text
font = pygame.font.SysFont("monospace", 65)

# Score of game
score = 100

# For game loop
done = False

# Stores time since the cursor moved / Since the spin ended
time_since_movement = 0

# To only run certain actions one (e.g setup)
initial = True

# Stores the visual graphics of each token
tokens_render = []


# returns a list that is ['a', 'b', 'c', 'd', ...]
letters = list('abcdefghijklmnopqrstuvwxyz')
command = ''

# Initializes the recognizer
recognizer = aiy.cloudspeech.get_recognizer()
# Starts the microphone
aiy.audio.get_recorder().start()
# Teaches the recognizer to expect these phrases
for letter in letters:
    recognizer.expect_phrase("letter " + letter)
recognizer.expect_phrase("quit")


# Sets the coordinates for the cursor
def set_cursor_coords(x_pos, y_pos):
    global cursor_coords
    cursor_coords[0] = [x_pos, y_pos - 16]
    cursor_coords[1] = [x_pos + 16, y_pos - 16]
    cursor_coords[2] = [x_pos + 8, y_pos]


def get_solve_state(letter):
    print("Solve State Called")
    global solve_state, command, score
    # Convert the letter to an uppercase
    letter = letter.upper()
    # If letter does not exist in the solve state means it might be a potential solve
    if letter not in solve_state:
        # Stores positions of the letter than can be added into solve state
        indices = []
        # It looks at the answer variable, which is the solved word and finds the positions of the guessed letter from it
        for i, elem in enumerate(answer):
            if elem == letter:
                indices.append(i)
        for index in indices:
            # Converts the solve_state string variable into a list
            tmp = list(solve_state)
            # Change the underscore in the solve_state to the letter guessed
            tmp[index] = letter
            # Update solve_state
            solve_state = "".join(tmp)
        # If letter chosen isnt found anywhere in solve state
        if len(indices) == 0:
            aiy.audio.say("Letter not found")
            print("Not found :(")
            score -= 200
            command = ''
        else:
            print(solve_state)
            command = ''

    else:
        score -= 200
        print("ALREADY FOUND")


# Checks for winning / Losing condition: Score < 0 loss; all blanks filled = win
def winning_condition():
    global score, done, solve_state
    if score < 0:
        done = True

        aiy.audio.say("You Lost!")
        print("You ran out of money. You Lost!")
        return
    if "_" not in solve_state:
        done = True
        aiy.audio.say("You Won!")
        print("You Win!")
        return


# The main game loop
def start():
    aiy.audio.say("To start, press V and say a letter, or quit to exit")
    global done, command
    # While the done variable is equal to False, run this loop
    while not done:
        # Locks at 60fps
        clock.tick(60)
        for event in pygame.event.get():
            # If user presses the close button, set done to True and exit loop
            if event.type == pygame.QUIT:
                done = True
            # If user presses down a key
            if event.type == pygame.KEYDOWN:
                # If the key pressed is V
                if event.key == pygame.K_v:
                    print("Waiting for input")
                    process_text(get_text())
                # If the key pressed is C
                if event.key == pygame.K_c:
                    print("Waiting for answer")
                    # Call function guess_phrase()
                    guess_phrase()
        # Every 1/60th of a second, call render() and update()
        update()
        render()


# Creates a list that stores the graphic of the text, along with its coordinates
def create_tokens(token_list):
    # Starting coordinates to draw the tokens
    start_x = 64
    start_y = 64
    # Stores the text to be rendered (tokens with "$" sign)
    text_to_render = []
    # Add to text_to_render with each token value but with "$" sign added
    for token in token_list:
        text_to_render.append("$" + str(token))
    # Store width of rendered text
    txt_width = 0
    for txt in text_to_render:
        # Render the label with the color blue
        label = font.render(txt, True, blue)
        # Add the text graphic, it's x-coordinate and y-coordinate to tokens_render
        # tokens_render will now have [[label1, label1_x_coordinate, label1_y_coordinate], ...]
        tokens_render.append([label, start_x, start_y])
        # Get the width of the current token graphic
        txt_width = label.get_width()
        # Store coordinates of each rendered token
        token_coords.append([start_x, start_y])
        # add that width to start_x so that the next token that is rendered will not be overlapping the previous rendered token
        start_x += txt_width + 32


# Function to retrieve what was said to the voice kit
def get_text():
    text = recognizer.recognize()
    return text


# Pass in a string (from get_text() usually) to deduce what to do with it
def process_text(text):
    global command, done, letters
    text = text.lower()

    if not text:
        print("No audio heard")
        aiy.audio.say("No audio heard")
    else:
        print("Recognized Text: " + text)
        # If user says quit, end the game loop by setting the done variable to True
        if "quit" in text:
            done = True
        else:
            # Iterate through the list of alphabets
            for letter in letters:
                if "letter " + letter in text:
                    print("Letter is " + letter)
                    command = letter
                    break
                else:
                    print("Invalid")


def guess_phrase():
    global done
    text = recognizer.recognize()
    if not text:
        print("No audio heard")
        aiy.audio.say("No audio heard")
    else:
        print("Recognized Text: " + text)
        if text.lower() == answer.lower():
            done = True
            aiy.audio.say("You Won!")
            print("You Won!")


# Updates all the necessary data for the game
def update():
    global time_since_movement, token_coords, initial, command, score, tokens
    if initial is True:
        # Creates the graphic of the text of each token
        create_tokens(tokens)
        # Sets the coordinates of the cursor to the very first token
        set_cursor_coords(token_coords[0][0], token_coords[0][1])
        # Set inital to false as there is no need to call these variables again
        initial = False

    # clock.get_time() calculates the time since the last frame was called
    # time_since_movement keeps track of total time passed since cursor moved
    time_since_movement += clock.get_time()
    print("Command is " + command)
    winning_condition()
    if command:
        # If a command exists, it is probably to shuffle between tokens and guess a letter/solve
        res = shuffle_cursor(command)
        # Once shuffle_cursor returns the position of token that was chosen from the spin add that to the score
        if res:
            score += tokens[res]


# This stores the time you'd want the cursor to stay on the token before moving to another (when spinning)
delay = 100
# Alters the length of delay
acceleration = 1

# Method for cursor to move around and select a token
# Then returns the index of the token AKA the money he chose
# Call after spinning


def shuffle_cursor(letter):
    global time_since_movement, delay, acceleration
    chosen_coord = random.choice(token_coords)
    # If the time it stays on one token before moving to another in the shuffle is greater than 1 second, use that token
    if delay >= 1000:
        # Where you get input for letter
        get_solve_state(letter)
        # Returns position of the money won from the token list
        return token_coords.index(chosen_coord)
    else:
        # If the time since the cursor last moved is greater than delay variable, then move it to the randomnly chosen token
        if time_since_movement >= delay:
            # set the cursor coordinates to the coordinate of the chosen token
            set_cursor_coords(chosen_coord[0], chosen_coord[1])
            # Reset time since cursor moved to 0
            time_since_movement = 0
            # Increase the time requirement for cursor to move to next token
            delay += acceleration
            # So that delay variable gets considerably longer after each iteration
            acceleration *= 2


# Handles drawing to the screen
def render():
    global token_coords, cursor_coords, tokens_render
    # Clear screen by painting it completely white
    screen.fill(white)

    # Draw the progress of the sovle
    label = font.render(solve_state, True, blue)
    screen.blit(label, (screen_width/2 - label.get_width(),
                        screen_height - (label.get_height() / 2 * 3)))

    # Draw the current score
    score_font = font.render("Score: " + str(score), True, blue)
    screen.blit(score_font, (screen_width/2, screen_height/2))

    # Draws all the token graphics onto the screen
    for token in tokens_render:
        screen.blit(token[0], (token[1], token[2]))
    # Draw the cursor
    pygame.draw.polygon(screen, red, cursor_coords, 0)
    # Update scren
    pygame.display.flip()


def main():
    start()


if __name__ == '__main__':
    main()
