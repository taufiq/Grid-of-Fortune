import pygame
import random
import time
import aiy.audio
import aiy.cloudspeech
import aiy.voicehat

clock = pygame.time.Clock()
FPS = 60

white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

screen_width = 1000
screen_height = 1000

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
answer = "BANANA"

solve_state = ""

for char in answer:
    if char is not " ":
        solve_state += "_"
    else:
        solve_state += " "

wedges = [500, 200, 400, 100, 600, 450]
wedges_render = []
wedge_coords = []
cursor_coords = [[], [], []]
font = pygame.font.SysFont("monospace", 65)

score = 100
done = False
time_since_movement = 0
initial = True

letters = list('abcdefghijklmnopqrstuvwxyz')
command = ''

delay = 100
acceleration = 1

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
    result = True
    print("Solve State Called")
    global solve_state, command, score

    letter = letter.upper()
    if letter not in solve_state:
        indices = []
        for i, elem in enumerate(answer):
            if elem == letter:
                indices.append(i)
        for index in indices:
            tmp = list(solve_state)
            tmp[index] = letter
            solve_state = "".join(tmp)

        if len(indices) == 0:
            aiy.audio.say("Letter not found")
            print("Not found :(")
            score -= 200
            command = ''
            result = False
        else:
            print(solve_state)
            command = ''
    else:
        score -= 200
        print("ALREADY FOUND")
        result = False
    return result


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


def start():
    aiy.audio.say(
        "To start, press v and say a letter, press c and say the answer or quit to exit")
    global done, command
    while not done:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    print("Waiting for input")
                    process_text(get_text())
                if event.key == pygame.K_c:
                    print("Waiting for answer")
                    guess_phrase()

        update()
        render()


def create_wedges(wedge_list):
    start_x = 64
    start_y = 64
    text_to_render = []

    for wedge in wedge_list:
        text_to_render.append("$" + str(wedge))

    txt_width = 0
    for txt in text_to_render:
        label = font.render(txt, True, blue)
        wedges_render.append([label, start_x, start_y])
        txt_width = label.get_width()
        wedge_coords.append([start_x, start_y])
        start_x += txt_width + 32


def get_text():
    text = recognizer.recognize()
    return text


def process_text(text):
    global command, done, letters
    text = text.lower()

    if not text:
        print("No audio heard")
        aiy.audio.say("No audio heard")
    else:
        print("Recognized Text: " + text)
        if "quit" in text:
            done = True
        else:
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


def update():
    global time_since_movement, wedge_coords, initial, command, score, wedges
    if initial is True:
        create_wedges(wedges)
        set_cursor_coords(wedge_coords[0][0], wedge_coords[0][1])
        initial = False

    time_since_movement += clock.get_time()
    print("Command is " + command)
    winning_condition()
    if command:
        res = shuffle_cursor(command)
        if res:
            score += wedges[res]


def shuffle_cursor(letter):
    global time_since_movement, delay, acceleration
    chosen_coord = random.choice(wedge_coords)

    if delay >= 1000:
        correct = get_solve_state(letter)
        set_cursor_coords(chosen_coord[0], chosen_coord[1])
        acceleration = 1
        delay = 100
        if correct:
            return wedge_coords.index(chosen_coord)
    else:
        if time_since_movement >= delay:
            set_cursor_coords(chosen_coord[0], chosen_coord[1])
            time_since_movement = 0
            delay += acceleration
            acceleration *= 2


def render():
    global wedge_coords, cursor_coords, wedges_render
    screen.fill(white)
    label = font.render(solve_state, True, blue)
    screen.blit(label, (screen_width/2 - label.get_width(),
                        screen_height - (label.get_height() / 2 * 3)))
    score_font = font.render("Score: " + str(score), True, blue)
    screen.blit(score_font, (screen_width/2, screen_height/2))
    for wedge in wedges_render:
        screen.blit(wedge[0], (wedge[1], wedge[2]))
    pygame.draw.polygon(screen, red, cursor_coords, 0)
    pygame.display.flip()


def main():
    start()


if __name__ == '__main__':
    main()
