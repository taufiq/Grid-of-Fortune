import pygame

clock = pygame.time.Clock()
FPS = 60
# Colors
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

# Sizes
screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
window = pygame.display.get_surface()
answer = "DOPE LIES ARE GREAT"
solve_state = "".join(["_" if x is not " " else " " for x in answer])

pygame.init()
font = pygame.font.SysFont("monospace", 65)


def get_solve_state(letter):
    global solve_state
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
        else:
            print(solve_state)

    else:
        print("ALREADY FOUND")


def start():
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            update()
            render()


def update():
    pass


def render():
    clock.tick(60)
    screen.fill(white)
    label = font.render(solve_state, True, blue)
    screen.blit(label, (0, 0))
    print(solve_state)
    pygame.display.flip()


def main():

    start()


if __name__ == '__main__':
    main()


def get_command():
    # Get voice command
    return 'COMMAND'
