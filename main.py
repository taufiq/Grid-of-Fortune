import pygame
import random
import time
import aiy.audio
import aiy.cloudspeech
import aiy.voicehat

clock = pygame.time.Clock()
FPS = 60
MOVE_CURSOR = pygame.USEREVENT
# Colors
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

# Sizes
screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
answer = "DOPE LIES ARE GREAT"
solve_state = "".join(["_" if x is not " " else " " for x in answer])

token_coords = []
cursor_coords = [[], [], []]

pygame.init()
font = pygame.font.SysFont("monospace", 65)

done = False


letters = list('abcdefghijklmnopqrstuvwxyz')
command = ''

recognizer = aiy.cloudspeech.get_recognizer()
aiy.audio.get_recorder().start()
for letter in letters:
    recognizer.expect_phrase("letter " + letter)
recognizer.expect_phrase("quit")


def set_cursor_coords(x_pos, y_pos):
    global cursor_coords
    cursor_coords[0] = [x_pos, y_pos - 16]
    cursor_coords[1] = [x_pos + 16, y_pos - 16]
    cursor_coords[2] = [x_pos + 8, y_pos]


def get_solve_state(letter):
    print("Solve State Called")
    global solve_state, command
    letter = letter.upper()
    if letter not in solve_state:
        # Returns indices of found letter
        indices = [i for i, elem in enumerate(answer) if elem == letter]
        for index in indices:
            tmp = list(solve_state)
            tmp[index] = letter
            solve_state = "".join(tmp)
        # If letter chosen isnt found anywhere in solve state
        if len(indices) == 0:
            print("Not found :(")
            command = ''
        else:
            print(solve_state)
            command = ''

    else:
        print("ALREADY FOUND")


def start():
    global done, command
    while not done:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    print("V Pressed")
                    process_text(get_text())


        update()
        render()


time_since_movement = 0
count = 0


initial = True

labels_render = []


def create_tokens(token_list):
    start_x = 64
    start_y = 64
    text_to_render = map(lambda x: "$"+str(x), token_list)
    prev_width = 0
    for txt in text_to_render:
        label = font.render(txt, True, blue)
        labels_render.append([label, start_x, start_y])
        prev_width = label.get_width()
        token_coords.append([start_x, start_y])
        start_x += prev_width + 32

def get_text():
    text = recognizer.recognize()
    time.sleep(2)
    print("Recognized Text: " + text)
    return text

def process_text(text):
    global command, done, letters
    text = text.lower()

    if not text:
        print("No audio heard")
    else:
        if "quit" in text:
            done = True
        for letter in letters:
            if "letter " + letter in text:
                print("Letter is " + letter)
                command = letter
            else:
                print("Invalid")


def update():
    global time_since_movement, count, token_coords, initial, command
    if initial is True:
        create_tokens([500, 200, 400, 100, 600, 450])
        set_cursor_coords(token_coords[0][0], token_coords[0][1])
        initial = False
    time_since_movement += clock.get_time()
    print("Command is " + command)
    if command:
        shuffle_cursor(command)



delay = 100
acceleration = 10

# Method for cursor to move around and select a token
# Then returns the index of the token AKA the money he chose
# Call after spinning



def shuffle_cursor(letter):
    global time_since_movement, delay, acceleration
    chosen_coord = random.choice(token_coords)
    if delay >= 1000:
        # Where you get input for letter
        get_solve_state(letter)
        # Returns money won
        return token_coords.index(chosen_coord)
    else:
        if time_since_movement >= delay:
            set_cursor_coords(chosen_coord[0], chosen_coord[1])
            time_since_movement = 0
            delay += acceleration
            acceleration *= 2


def render():
    global token_coords, cursor_coords, labels_render
    screen.fill(white)

    label = font.render(solve_state, True, blue)
    screen.blit(label, (screen_width/2 - label.get_width(),
                        screen_height - (label.get_height() / 2 * 3)))
    for label in labels_render:
        screen.blit(label[0], (label[1], label[2]))
    pygame.draw.polygon(screen, red, cursor_coords, 0)
    pygame.display.flip()


def main():
    start()


if __name__ == '__main__':
    main()



