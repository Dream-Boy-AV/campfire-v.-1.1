import os
import sys
import math
import random
import pygame
from pygame.locals import SRCALPHA


def load_image(name):
    # Function for more convenient image loading
    fullname = os.path.join('graphics', name)
    image = pygame.image.load(fullname)
    return image


def screen_setting():
    # Screen size config

    global screen, DISPLAY_SURFACE, FUNCTIONAL_SURFACE, cur_size

    cur_size = monitor_size if fullscreen else SIZE

    if fullscreen:
        screen = pygame.display.set_mode(cur_size, pygame.FULLSCREEN)  # Basic display
    else:
        screen = pygame.display.set_mode(cur_size)
    DISPLAY_SURFACE = pygame.display.set_mode(cur_size)  # Additional blank display
    FUNCTIONAL_SURFACE = pygame.Surface(cur_size,
                                        flags=SRCALPHA)  # Functional display for pop-up windows


def popup_config():
    # Pop-up window configs
    global popup_image_size, yes_no_btn_size, done_btn_size, checkbox_size
    global popup_image, yes_btn, no_btn, done_btn, fs_checkbox_ch, fs_checkbox_un

    popup_image_size = round(0.622 * cur_size[0]), round(0.6344 * cur_size[1])
    yes_no_btn_size = round(0.2213 * cur_size[0]), round(0.1722 * cur_size[1])
    done_btn_size = round(0.1772 * cur_size[0]), round(0.0976 * cur_size[1])
    checkbox_size = round(0.0313 * cur_size[0]), round(0.0556 * cur_size[1])
    popup_image = pygame.transform.scale(load_image('textures\\pop-up_bcg.png'), popup_image_size)
    yes_btn = pygame.transform.scale(load_image('icons\\dia_btn_yes.png'), yes_no_btn_size)
    no_btn = pygame.transform.scale(load_image('icons\\dia_btn_no.png'), yes_no_btn_size)
    done_btn = pygame.transform.scale(load_image('icons\\options_done_btn.png'), done_btn_size)
    fs_checkbox_ch = pygame.transform.scale(load_image('icons\\options_checkbox_checked.png'),
                                            checkbox_size)
    fs_checkbox_un = pygame.transform.scale(load_image('icons\\options_checkbox_unchecked.png'),
                                            checkbox_size)

    global pause_btn_size, pause_buttons, cont_image, cont, restart_image, restart, ext_image, ext

    # Pause buttons:
    pause_btn_size = round(0.0969 * cur_size[0]), round(0.1722 * cur_size[1])
    pause_buttons = pygame.sprite.Group()
    cont_image = pygame.transform.scale(load_image('icons\\pause_continue_btn.png'), pause_btn_size)
    cont = pygame.sprite.Sprite(pause_buttons)
    cont.image = cont_image
    cont.rect = cont.image.get_rect()
    cont.rect.x, cont.rect.y = round(0.3313 * cur_size[0]), round(0.5211 * cur_size[1])

    restart_image = pygame.transform.scale(load_image('icons\\pause_restart_btn.png'),
                                           pause_btn_size)
    restart = pygame.sprite.Sprite(pause_buttons)
    restart.image = restart_image
    restart.rect = restart.image.get_rect()
    restart.rect.x, restart.rect.y = round(0.4522 * cur_size[0]), round(0.5211 * cur_size[1])

    ext_image = pygame.transform.scale(load_image('icons\\pause_exit_btn.png'), pause_btn_size)
    ext = pygame.sprite.Sprite(pause_buttons)
    ext.image = ext_image
    ext.rect = ext.image.get_rect()
    ext.rect.x, ext.rect.y = round(0.5731 * cur_size[0]), round(0.5211 * cur_size[1])


# Initializing Pygame
pygame.init()
pygame.display.set_caption('campfire')
FPS = 50  # FPS value for animations

# Display initializing
monitor_size = pygame.display.get_desktop_sizes()[0]
display_modes = [(2560, 1440), (2048, 1152), (1920, 1080), (1600, 900), (1366, 768), (1280, 720),
                 (960, 540)]
fitting = [abs(monitor_size[0] - mode[0]) for mode in display_modes]
SIZE = WIDTH, HEIGHT = display_modes[fitting.index(min(fitting)) + 1]\
    if fitting.index(min(fitting)) != 6 else monitor_size
cur_size = None

# Saved data unpacking
with open('save_data.txt', 'r') as sd:
    data = sd.readlines()
    bgm_volume = int(data[2][7:].rstrip('\n'))
    sound_volume = int(data[3][7:].rstrip('\n'))
    fullscreen = False if data[4][12] == '0' else True
screen, DISPLAY_SURFACE, FUNCTIONAL_SURFACE = None, None, None
screen_setting()

# Basic components initializing
save = []
chip_names = ['blue', 'green', 'red', 'yellow']  # Names for chips to choose from
game_on, menu, time_running = False, False, False  # Interface determinants
clock = pygame.time.Clock()
pygame.display.set_icon(load_image('textures\\icon.png'))

hint_in_image = load_image('icons\\level_hint_btn_off.png')
hint_act_image = load_image('icons\\level_hint_btn.png')
hint_image = hint_in_image

# Initializing pop-up window configs
popup_image_size, yes_no_btn_size, done_btn_size, checkbox_size = (), (), (), ()
popup_image, yes_btn, no_btn, done_btn, fs_checkbox_ch, fs_checkbox_un = None, None, None, None, \
                                                                         None, None
pause_btn_size, pause_buttons, cont_image, cont = (), None, None, None
restart_image, restart, ext_image, ext = None, None, None, None
popup_config()

# Initializing chip containers and other global elements
chips_list = []
chips = pygame.sprite.Group()
cells = pygame.sprite.Group()
lv, goal_image, count_text, counter, time, timer = None, None, None, None, None, None
closed_cell, opened_cell = None, None
goal_name = None
match_particle, win_particle = None, None
gamemode = 0
new_game = False
hint_counter, coal_counter = 0, 0
got_hint, deleted, replaced = False, False, None

# Initializing sound system
pygame.mixer.init()
song = pygame.mixer.Sound('sounds\\songs\\menu_song.mp3')

BTN_CLICK = pygame.mixer.Sound('sounds\\effects\\button_push.mp3')
CHIP_CLICK = pygame.mixer.Sound('sounds\\effects\\chip_push.mp3')
MATCH_SND = pygame.mixer.Sound('sounds\\effects\\chip_match.mp3')
MISSION_SND = pygame.mixer.Sound('sounds\\effects\\mission_fill.mp3')
RETURN_SND = pygame.mixer.Sound('sounds\\effects\\chip_return.mp3')
HINT_SND = pygame.mixer.Sound('sounds\\effects\\hint_appears.mp3')
START_SND = pygame.mixer.Sound('sounds\\effects\\game_start.mp3')
WIN_SND = pygame.mixer.Sound('sounds\\effects\\win.mp3')
FAIL_SND = pygame.mixer.Sound('sounds\\effects\\fail.mp3')


def sound_volume_set(percent):
    sounds = [BTN_CLICK, CHIP_CLICK, MATCH_SND, MISSION_SND,
              RETURN_SND, HINT_SND, START_SND, WIN_SND, FAIL_SND]
    for sound in sounds:
        sound.set_volume(percent / 100)


# Setting correct volume for sounds
sound_volume_set(sound_volume)

# Initializing timer event
timer_event = pygame.USEREVENT + 1


class Particle:
    # Class for cell clearing particles

    def __init__(self):
        self.particles = []
        self.size = self.width, self.height = round(0.011 * cur_size[0]), round(
            0.0195 * cur_size[1])
        self.surface = pygame.transform.scale(load_image('effects\\sparkle_pcl.png'), self.size)

    def emit(self):
        # Moves and draw particles
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0].x += particle[1]
                particle[0].y += particle[2]
                particle[3] = round(particle[3] - 0.4, 1)
                screen.blit(self.surface, particle[0])

    def add_particles(self, x, y, size):
        # Adds particles
        lifetime = 1.2
        center_x, center_y = size * 3 // 8 + x, size // 4 + y
        route = 0.25 * size
        for i in range(8):
            angle = round(math.pi / 4 * i, 4)
            direction_x = round(math.cos(angle) * route)
            direction_y = round(-math.sin(angle) * route)
            particle_rect = pygame.Rect(center_x, center_y, self.width, self.height)
            self.particles += [[particle_rect, direction_x, direction_y, lifetime]]

    def delete_particles(self):
        # Deletes particles after a certain amount of time
        particle_copy = [particle for particle in self.particles if particle[3] > 0]
        self.particles = particle_copy


class WinParticle:
    # Class for level clearing particles

    def __init__(self):
        self.particles = []
        self.size = self.width, self.height = round(0.022 * cur_size[0]), round(
            0.039 * cur_size[1])
        self.surface = pygame.transform.scale(load_image('effects\\sparkle_pcl.png'), self.size)

    def emit(self):
        # Moves and draw particles
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0].x += particle[1]
                particle[0].y += particle[2]
                particle[3] = round(particle[3] - 0.2, 1)
                screen.blit(self.surface, particle[0])

    def add_particles(self, x, y):
        # Adds particles
        size = round(0.0586 * cur_size[0])
        lifetime = 1.2
        center_x, center_y = x, y
        route = 0.125 * size
        for i in range(12):
            angle = round(math.pi / 6 * i, 4)
            direction_x = round(math.cos(angle) * route)
            direction_y = round(-math.sin(angle) * route)
            particle_rect = pygame.Rect(center_x, center_y, self.width, self.height)
            self.particles += [[particle_rect, direction_x, direction_y, lifetime]]

    def delete_particles(self):
        # Deletes particles after a certain amount of time
        particle_copy = [particle for particle in self.particles if particle[3] > 0]
        self.particles = particle_copy


class Chip:
    # Special class for playable chip on field.

    def __init__(self, name, coords, group):
        self.name = name
        self.size = self.width, self.height = round(0.0438 * cur_size[0]), round(0.0778 *
                                                                                 cur_size[1])
        self.x, self.y = coords
        self.original_coords = coords
        self.move_direction = None
        self.group = group

        self.image = load_image('icons\\chip_{}.png'.format(self.name))
        self.sprite = pygame.sprite.Sprite(self.group)

        self.sprite_def()
        self.chosen = False

    def sprite_def(self):
        # Initializing chip sprite
        self.sprite.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.x, self.sprite.rect.y = self.x, self.y

    def __eq__(self, other):
        # Method for matching comparison
        return self.name == other.name

    def __str__(self):
        # Method for convenient (debug) presentation
        return self.name

    def choose(self):
        # Method for visual choose of chip
        if self.chosen:
            self.width += round(0.003 * cur_size[0])
            self.height += round(0.005 * cur_size[1])
            self.x -= round(0.001 * cur_size[0])
            self.y -= round(0.003 * cur_size[1])
        else:
            self.width -= round(0.003 * cur_size[0])
            self.height -= round(0.005 * cur_size[1])
            self.x += round(0.001 * cur_size[0])
            self.y += round(0.003 * cur_size[1])
        self.sprite_def()
        self.chosen = not self.chosen
        CHIP_CLICK.play()

    def ischosen(self):
        # Method to check if this chip is chosen
        return self.chosen

    def move(self, x, y):
        # Method to visually move chip
        if self.move_direction == 'swap':
            self.sprite.rect.x, self.sprite.rect.y = x, y
            self.x, self.y = x, y
            self.move_direction = None
        else:
            self.direction_def(x, y)
            if self.move_direction == 'hor':
                self.sprite.rect.y = self.original_coords[1]
                self.y = self.original_coords[1]
                exp_dx = round(0.059 * cur_size[0])
                if abs(self.original_coords[0] - x) <= exp_dx:
                    exp_dx = x - self.original_coords[0]
                elif self.original_coords[0] - x > 0:
                    exp_dx = -exp_dx
                self.sprite.rect.x = self.original_coords[0] + exp_dx
                self.x = self.original_coords[0] + exp_dx
            elif self.move_direction == 'ver':
                self.sprite.rect.x = self.original_coords[0]
                self.x = self.original_coords[0]
                exp_dy = round(0.105 * cur_size[1])
                if abs(self.original_coords[1] - y) <= exp_dy:
                    exp_dy = y - self.original_coords[1]
                elif self.original_coords[1] - y > 0:
                    exp_dy = -exp_dy
                self.sprite.rect.y = self.original_coords[1] + exp_dy
                self.y = self.original_coords[1] + exp_dy

    def direction_def(self, x, y):
        # Moving left or right
        if abs(x - self.original_coords[0]) > abs(y - self.original_coords[1]):
            self.move_direction = 'hor'
        # Moving up or down
        elif abs(y - self.original_coords[1]) > abs(x - self.original_coords[0]):
            self.move_direction = 'ver'

    def prep_to_swap(self):
        # Prepares chip to swap with other chip
        self.move_direction = 'swap'

    def set_orig(self, coord):
        # Changes original coordinates for chip, setting a new start position for it
        self.original_coords = coord

    def set_original_pos(self):
        # Returns chip to it's original position
        self.sprite.rect.x, self.sprite.rect.y = self.original_coords
        self.x, self.y = self.original_coords
        self.move_direction = None

    def disappear(self):
        # Method to set a transparent texture to chip simulating it's disappearance

        # Blank texture
        txr_size = round(0.0512 * cur_size[0]), round(0.0911 * cur_size[1])
        blank = pygame.transform.scale(load_image('effects\\blank.png'), txr_size)
        self.sprite.image = blank

    def appear(self):
        # Method to set a native texture to chip simulating it's appearance
        self.sprite.image = self.image

    def set_image(self, name):
        self.name = name
        self.image = load_image('icons\\chip_{}.png'.format(self.name))


class Slider:
    # Class of volume option slider

    def __init__(self, var):
        self.axis_image = load_image('icons\\options_slider_line.png')
        self.button_image = load_image('icons\\options_slider_btn.png')
        self.var = var
        self.axis, self.button, self.button_size = None, None, None
        self.axis_coords, self.button_coords = None, None

    def position_def_draw(self, percent):
        # Position definition and instant drawing

        axis_size = round(0.4534 * cur_size[0]), round(0.0167 * cur_size[1])
        self.button_size = round(0.0313 * cur_size[0]), round(0.0556 * cur_size[1])
        self.axis = pygame.transform.scale(self.axis_image, axis_size)
        self.button = pygame.transform.scale(self.button_image, self.button_size)

        axis_y = round(0.4444 * cur_size[1]) if self.var == 'bgm' else round(0.5656 * cur_size[1])
        button_y = round(0.4225 * cur_size[1]) if self.var == 'bgm' else round(0.545 * cur_size[1])
        button_pos = 0.4444 * cur_size[0] * percent / 100
        self.axis_coords = round(0.2815 * cur_size[0]), axis_y
        self.button_coords = [0.2703 * cur_size[0] + button_pos, button_y]
        self.draw()

    def draw(self):
        # Blit function

        screen.blit(self.axis, self.axis_coords)
        screen.blit(self.button, (round(self.button_coords[0]), self.button_coords[1]))

    def move(self, x):
        # Function for slider button position changing

        if 0.2703 * cur_size[0] <= self.button_coords[0] - x <= 0.7147 * cur_size[0]:
            self.button_coords[0] -= x
            pos = self.button_coords[0] - 0.2703 * cur_size[0]
            percent = round(pos / cur_size[0] / 0.4444 * 100)
            if self.var == 'bgm':
                self.bgm_vol_set(percent)
            else:
                self.sound_vol_set(percent)

    def bgm_vol_set(self, percent):
        # Function to set and save BGM volume

        global bgm_volume
        bgm_volume = percent
        song.set_volume(bgm_volume / 100)

        with open('save_data.txt', 'r') as sd:
            savedata = sd.readlines()
            savedata1 = savedata[:2]
            savedata2 = savedata[3:]
        with open('save_data.txt', 'w') as sd:
            to_write = ''.join(savedata1) + 'music: {}\n'.format(str(bgm_volume)
                                                                 ) + ''.join(savedata2)
            sd.write(to_write)

    def sound_vol_set(self, percent):
        # Function to set and save sound volume

        global sound_volume
        sound_volume = percent
        sound_volume_set(sound_volume)

        with open('save_data.txt', 'r') as sd:
            savedata = sd.readlines()
            savedata1 = savedata[:3]
            savedata2 = savedata[4]
        with open('save_data.txt', 'w') as sd:
            to_write = ''.join(savedata1) + 'sound: {}\n'.format(str(sound_volume)) + savedata2
            sd.write(to_write)

    def get_button_rect(self):
        # Function returning slider geometric info for movement purposes

        return self.button_coords, self.button_size[0], self.axis_coords


def game():
    global menu, new_game, song, game_on, time_running, screen, fullscreen, match_particle, cur_size, time
    global replaced
    # Base game function

    # Starting game with the main menu
    main_menu()
    dx, dy = 0, 0
    chosen_chip = None
    helping, options, exit_popup, odd_click = False, False, False, False
    lev_pause, lev_options, lev_restart, lev_exit, game_over = False, False, False, False, False
    finish = False
    win_particle = WinParticle()
    bgm_slider = Slider('bgm')
    snd_slider = Slider('sound')
    clicked, lock_x = False, 0
    while True:
        for event in pygame.event.get():
            # if user quits, termination function starts
            if event.type == pygame.QUIT:
                terminate()
            if menu:
                # if user is in main menu
                if odd_click:
                    odd_click = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    for btn in menu_buttons:
                        # if user clicks buttons, respective function starts
                        if btn.rect.x < ev_x < btn.rect.x + btn.rect.width \
                                and btn.rect.y < ev_y < btn.rect.y + btn.rect.height:
                            BTN_CLICK.play()
                            if btn.function == 'exit':
                                # "Exit" button shows quiting dialog
                                form_dialogue('yes_no')
                                popup_font = pygame.font.SysFont('impact',
                                                                 round(0.0729 * cur_size[1]))
                                message = popup_font.render('Do you really want to quit?',
                                                            1, pygame.Color('#F9F9E8'))
                                message_pos = round(
                                    0.6223 * cur_size[0] - message.get_rect().width) // 2 + round(
                                    0.193 * cur_size[0]), round(0.286 * cur_size[1])
                                FUNCTIONAL_SURFACE.blit(message, message_pos)
                                screen.blit(FUNCTIONAL_SURFACE, (0, 0))

                                menu = False
                                exit_popup = True
                            elif btn.function == 'ng':
                                # "New Game" button shows new game starting dialog
                                form_dialogue('yes_no')
                                popup_font = pygame.font.SysFont('impact',
                                                                 round(0.065 * cur_size[1]))
                                message1 = popup_font.render(
                                    'Do you really want to start a new game?', 1,
                                    pygame.Color('#F9F9E8'))

                                message2 = popup_font.render(
                                    '(All the current progress will be lost!)', 1,
                                    pygame.Color('#F9F9E8'))

                                message1_pos = round(
                                    0.6223 * cur_size[0] - message1.get_rect().width) // 2 + round(
                                    0.193 * cur_size[0]), round(0.2864 * cur_size[1])

                                message2_pos = round(
                                    0.6223 * cur_size[0] - message2.get_rect().width) // 2 + round(
                                    0.193 * cur_size[0]), round(0.3646 * cur_size[1])

                                FUNCTIONAL_SURFACE.blit(message1, message1_pos)
                                FUNCTIONAL_SURFACE.blit(message2, message2_pos)
                                screen.blit(FUNCTIONAL_SURFACE, (0, 0))
                                menu = False
                                new_game = True
                                odd_click = True
                            elif btn.function == 'cont':
                                # "Continue" button starts gameplay level from savedata
                                level_init()
                            elif btn.function == 'help':
                                # "Help" button shows basics window
                                form_dialogue()
                                popup_font = pygame.font.SysFont('impact',
                                                                 round(0.0313 * cur_size[1]))
                                heading = pygame.font.SysFont(
                                    'impact', round(0.09375 * cur_size[1])).render(
                                    'Help', 1, pygame.Color('#F9F9E8'))
                                heading_pos = round(0.6222 * cur_size[0] - heading.get_rect().width
                                                    ) // 2 + 0.1925 * cur_size[0], round(
                                    0.1953 * cur_size[1])
                                FUNCTIONAL_SURFACE.blit(heading, heading_pos)

                                im1_size = round(0.1281 * cur_size[0]), round(0.147 * cur_size[1])
                                im1_pos = round(0.2145 * cur_size[0]), round(0.3125 * cur_size[1])
                                im1 = pygame.transform.scale(load_image('textures\\help1.jpg'),
                                                             im1_size)
                                FUNCTIONAL_SURFACE.blit(im1, im1_pos)

                                im2_size = round(0.0967 * cur_size[0]), round(0.237 * cur_size[1])
                                im2_pos = round(0.2145 * cur_size[0]), round(0.4688 * cur_size[1])
                                im2 = pygame.transform.scale(load_image('textures\\help2.jpg'),
                                                             im2_size)
                                FUNCTIONAL_SURFACE.blit(im2, im2_pos)

                                im3_size = round(0.077 * cur_size[0]), round(0.213 * cur_size[1])
                                im3_pos = round(0.4758 * cur_size[0]), round(0.4688 * cur_size[1])
                                im3 = pygame.transform.scale(load_image('textures\\help3.jpg'),
                                                             im3_size)
                                FUNCTIONAL_SURFACE.blit(im3, im3_pos)

                                text = ['campfire is a match-3 game. Match 3 or more ',
                                        'identical figures on the field to complete the mission.',
                                        'When the mission is',
                                        'complete, you will', 'finish the level.',
                                        'But if the timer ', 'runs out, you lose.',
                                        'Use the pause button', 'to pause the game.',
                                        'Use the hint button', 'to delete some chips,',
                                        'if you cannot find any matches.']
                                text_pos = [(0.3514, 0.3255), (0.3514, 0.3646), (0.3221, 0.4688),
                                            (0.3221, 0.5078), (0.3221, 0.5469), (0.3221, 0.5859),
                                            (0.3221, 0.625), (0.571, 0.4688), (0.571, 0.5078),
                                            (0.571, 0.5468), (0.571, 0.5858), (0.571, 0.625)]
                                text_pos = [(round(x * cur_size[0]),
                                             round(y * cur_size[1])) for x, y in text_pos]
                                for i in range(len(text)):
                                    surf = popup_font.render(text[i], 1, pygame.Color('#F9F9E8'))
                                    FUNCTIONAL_SURFACE.blit(surf, text_pos[i])

                                screen.blit(FUNCTIONAL_SURFACE, (0, 0))

                                menu = False
                                helping = True
                            elif btn.function == 'options':
                                # "Options" button shows options window
                                options_form()
                                bgm_slider.position_def_draw(bgm_volume)
                                snd_slider.position_def_draw(sound_volume)
                                menu = False
                                options = True
                                odd_click = True
            elif game_on:
                # if user is playing a level
                level_btn_size = round(0.0688 * cur_size[0]), round(0.1222 * cur_size[1])
                pause_btn_pos = round(0.1219 * cur_size[0]), round(0.7956 * cur_size[1])
                hint_btn_pos = round(0.1219 * cur_size[0]), round(0.6526 * cur_size[1])

                check_matches()
                if int(count_text[:count_text.find('/')]) \
                        >= int(count_text[count_text.find('/') + 1:]):
                    # Opens "You won" pop-up window
                    pygame.time.set_timer(timer_event, 0)
                    song.stop()
                    WIN_SND.play()

                    stars1_pos = round(0.2635 * cur_size[0]), round(0.26 * cur_size[1])
                    stars2_pos = round(0.7269 * cur_size[0]), round(0.26 * cur_size[1])
                    win_particle.add_particles(*stars1_pos)
                    win_particle.add_particles(*stars2_pos)

                    game_on = False
                    finish = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    # Button clicks start respective functions
                    if pause_btn_pos[0] < ev_x < pause_btn_pos[0] + level_btn_size[0] \
                            and pause_btn_pos[1] < ev_y < pause_btn_pos[1] + level_btn_size[1]:
                        BTN_CLICK.play()
                        # "Pause" button shows pause window
                        heading = pygame.font.SysFont('impact',
                                                      round(0.09375 * cur_size[1])).render(
                            'Paused', 1, pygame.Color('#F9F9E8'))
                        heading_pos = round(0.6223 * cur_size[0] - heading.get_rect().width) // 2 + \
                                      round(0.193 * cur_size[0]), round(0.245 * cur_size[1])
                        window_pos = round(0.1889 * cur_size[0]), round(0.1823 * cur_size[1])

                        FUNCTIONAL_SURFACE.blit(popup_image, window_pos)
                        FUNCTIONAL_SURFACE.blit(heading, heading_pos)
                        pause_buttons.draw(FUNCTIONAL_SURFACE)
                        screen.blit(FUNCTIONAL_SURFACE, (0, 0))

                        time_running = False
                        game_on = False
                        lev_pause = True
                    elif hint_btn_pos[0] < ev_x < hint_btn_pos[0] + level_btn_size[0] \
                            and hint_btn_pos[1] < ev_y < hint_btn_pos[1] + level_btn_size[1]:
                        # "Hint" button shows a hint
                        if got_hint:
                            hint()
                    else:
                        # Chip click makes the chip chosen
                        for chip in chips_list:
                            if chip.sprite.rect.x < ev_x < chip.sprite.rect.x + \
                                    chip.sprite.rect.width and chip.sprite.rect.y < ev_y \
                                    < chip.sprite.rect.y + chip.sprite.rect.height:
                                chip.choose()
                                chosen_chip = chip
                                if chip.ischosen():
                                    dx, dy = event.pos[0] - chip.sprite.rect.x, \
                                             event.pos[1] - chip.sprite.rect.y
                                else:
                                    chosen_chip = None
                                break
                if event.type == pygame.MOUSEMOTION and chosen_chip:
                    # Moving the chosen chip
                    x, y = pygame.mouse.get_pos()
                    x, y = x - dx, y - dy
                    chosen_chip.move(x, y)
                    matching_chip = None
                    match_list = pygame.sprite.spritecollide(chosen_chip.sprite, chips, False)
                    if len(match_list) == 2:
                        matching_chip_sprite = match_list[0] if match_list[0] != chosen_chip.sprite \
                            else match_list[-1]
                        for chip in chips_list:
                            if chip != chosen_chip and chip.sprite.rect == matching_chip_sprite.rect:
                                matching_chip = chip
                                break
                    if matching_chip:
                        chosen_chip.choose()
                        replace(chosen_chip, matching_chip)
                        chosen_chip = None
                if event.type == pygame.MOUSEBUTTONUP:
                    # Canceling the unfinished move
                    if chosen_chip:
                        chosen_chip.choose()
                        chosen_chip.set_original_pos()
                    chosen_chip = None
            elif exit_popup:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    if round(0.2679 * cur_size[0]) < ev_x < round(0.2679 * cur_size[0]) \
                            + yes_no_btn_size[0] and round(0.5482 * cur_size[1]) < \
                            ev_y < round(0.5482 * cur_size[1]) + yes_no_btn_size[1]:
                        BTN_CLICK.play()
                        terminate()
                    elif round(0.51 * cur_size[0]) < ev_x < round(0.51 * cur_size[0]) + \
                            yes_no_btn_size[0] and round(0.5482 * cur_size[1]) < \
                            ev_y < round(0.5482 * cur_size[1]) + yes_no_btn_size[1]:
                        BTN_CLICK.play()
                        exit_popup = False
                        main_menu()
            elif new_game:
                if odd_click:
                    odd_click = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    if round(0.2679 * cur_size[0]) < ev_x < round(0.2679 * cur_size[0]) \
                            + yes_no_btn_size[0] and round(0.5482 * cur_size[1]) < \
                            ev_y < round(0.5482 * cur_size[1]) + yes_no_btn_size[1]:
                        BTN_CLICK.play()
                        newgame()
                    elif round(0.51 * cur_size[0]) < ev_x < round(0.51 * cur_size[0]) + \
                            yes_no_btn_size[0] and round(0.5482 * cur_size[1]) < \
                            ev_y < round(0.5482 * cur_size[1]) + yes_no_btn_size[1]:
                        BTN_CLICK.play()
                        new_game = False
                        main_menu()
            elif helping or options:
                if odd_click:
                    odd_click = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    if round(0.4165 * cur_size[0]) < ev_x < round(0.4165 * cur_size[0]) \
                            + done_btn_size[0] and round(0.6862 * cur_size[1]) < ev_y < \
                            round(0.6862 * cur_size[1]) + done_btn_size[1]:
                        BTN_CLICK.play()
                        helping, options = False, False
                        main_menu()
                if options:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        ev_x, ev_y = event.pos
                        if round(0.2703 * cur_size[0]) < ev_x < round(0.2703 * cur_size[0]) \
                                + checkbox_size[0] and round(0.612 * cur_size[1]) < ev_y < \
                                round(0.612 * cur_size[1]) + checkbox_size[1]:
                            BTN_CLICK.play()
                            fullscreen_set()
                            popup_config()
                            options_form()
                            bgm_slider.position_def_draw(bgm_volume)
                            snd_slider.position_def_draw(sound_volume)
                            menu = False
                            options = True
                            odd_click = True
                        elif not clicked:
                            clicked, lock_x = True, ev_x
                    if event.type == pygame.MOUSEMOTION and clicked:
                        ev_x, ev_y = event.pos
                        bgm_btn_rect = bgm_slider.get_button_rect()
                        snd_btn_rect = snd_slider.get_button_rect()
                        bcg_x = round(0.1889 * cur_size[0])
                        if (bgm_btn_rect[0][1] < ev_y < bgm_btn_rect[0][1] + bgm_btn_rect[1]
                            or snd_btn_rect[0][1] < ev_y < snd_btn_rect[0][1] + snd_btn_rect[1]) \
                                and bcg_x < ev_x < bcg_x + popup_image_size[0]:
                            if bgm_btn_rect[0][1] < ev_y < bgm_btn_rect[0][1] + bgm_btn_rect[1]:
                                bgm_slider.move(lock_x - ev_x)
                            else:
                                snd_slider.move(lock_x - ev_x)
                            BTN_CLICK.play()
                            lock_x -= lock_x - ev_x
                            options_form()
                            bgm_slider.draw()
                            snd_slider.draw()
                    elif event.type == pygame.MOUSEBUTTONUP and clicked:
                        clicked, lock_x = False, 0
            elif lev_pause:
                if odd_click:
                    odd_click = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    if round(0.3302 * cur_size[0]) < ev_x < round(0.3302 * cur_size[0]) +\
                            pause_btn_size[0] and round(0.522 * cur_size[1]) < \
                            ev_y < round(0.522 * cur_size[1]) + pause_btn_size[1]:
                        BTN_CLICK.play()
                        time_running = True
                        lev_pause = False
                        game_on = True
                    elif round(0.4517 * cur_size[0]) < ev_x < round(0.4517 * cur_size[0]) + \
                            pause_btn_size[0] and round(0.522 * cur_size[1]) < \
                            ev_y < round(0.522 * cur_size[1]) + pause_btn_size[1]:
                        BTN_CLICK.play()
                        # "Restart" button shows restarting dialog
                        form_dialogue('yes_no')
                        popup_font = pygame.font.SysFont('impact', round(0.0651 * cur_size[1]))
                        message1 = popup_font.render('Do you really want to restart?', 1,
                                                     pygame.Color('#F9F9E8'))

                        message2 = popup_font.render('(All the current progress will be lost!)',
                                                     1, pygame.Color('#F9F9E8'))

                        message1_pos = round(0.6223 * cur_size[0] - message1.get_rect().width
                                             ) // 2 + round(0.193 * cur_size[0]), round(
                            0.2864 * cur_size[1])

                        message2_pos = round(0.6223 * cur_size[0] - message2.get_rect().width
                                             ) // 2 + round(0.193 * cur_size[0]), round(
                            0.3646 * cur_size[1])

                        FUNCTIONAL_SURFACE.blit(message1, message1_pos)
                        FUNCTIONAL_SURFACE.blit(message2, message2_pos)
                        screen.blit(FUNCTIONAL_SURFACE, (0, 0))
                        lev_pause = False
                        lev_restart = True
                        odd_click = True
                    elif round(0.5732 * cur_size[0]) < ev_x < round(0.5732 * cur_size[0]) \
                            + pause_btn_size[0] and round(0.522 * cur_size[1]) < \
                            ev_y < round(0.522 * cur_size[1]) + pause_btn_size[1]:
                        BTN_CLICK.play()
                        # "Exit" button shows dialog about returning to main menu
                        form_dialogue('yes_no')
                        popup_font = pygame.font.SysFont('impact', round(0.065 * cur_size[1]))
                        message1 = popup_font.render('Do you really want to return', 1,
                                                     pygame.Color('#F9F9E8'))

                        message1_5 = popup_font.render('to main menu?', 1, pygame.Color('#F9F9E8'))

                        message2 = popup_font.render('(All the current progress will be lost!)',
                                                     1, pygame.Color('#F9F9E8'))

                        message1_pos = round(
                            0.6223 * cur_size[0] - message1.get_rect().width) // 2 + round(
                            0.193 * cur_size[0]), round(0.2604 * cur_size[1])

                        message1_5_pos = round(
                            0.6223 * cur_size[0] - message1_5.get_rect().width) // 2 + round(
                            0.193 * cur_size[0]), round(0.3385 * cur_size[1])

                        message2_pos = round(
                            0.6223 * cur_size[0] - message2.get_rect().width) // 2 + round(
                            0.193 * cur_size[0]), round(0.4167 * cur_size[1])

                        FUNCTIONAL_SURFACE.blit(message1, message1_pos)
                        FUNCTIONAL_SURFACE.blit(message1_5, message1_5_pos)
                        FUNCTIONAL_SURFACE.blit(message2, message2_pos)
                        screen.blit(FUNCTIONAL_SURFACE, (0, 0))
                        lev_pause = False
                        lev_exit = True
                        odd_click = True
            elif lev_restart:
                if odd_click:
                    odd_click = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    if round(0.2679 * cur_size[0]) < ev_x < round(0.2679 * cur_size[0]) \
                            + yes_no_btn_size[0] and round(0.5482 * cur_size[1]) < \
                            ev_y < round(0.5482 * cur_size[1]) + yes_no_btn_size[1]:
                        BTN_CLICK.play()
                        lev_restart = False
                        level_init()
                    elif round(0.51 * cur_size[0]) < ev_x < round(0.51 * cur_size[0]) + \
                            yes_no_btn_size[0] and round(0.5482 * cur_size[1]) < \
                            ev_y < round(0.5482 * cur_size[1]) + yes_no_btn_size[1]:
                        BTN_CLICK.play()
                        lev_restart = False
                        time_running = True
                        game_on = True
            elif lev_exit:
                if odd_click:
                    odd_click = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    if round(0.2679 * cur_size[0]) < ev_x < round(0.2679 * cur_size[0]) \
                            + yes_no_btn_size[0] and round(0.5482 * cur_size[1]) < \
                            ev_y < round(0.5482 * cur_size[1]) + yes_no_btn_size[1]:
                        BTN_CLICK.play()
                        lev_exit = False
                        odd_click = True
                        main_menu()
                    elif round(0.51 * cur_size[0]) < ev_x < round(0.51 * cur_size[0]) + \
                            yes_no_btn_size[0] and round(0.5482 * cur_size[1]) < \
                            ev_y < round(0.5482 * cur_size[1]) + yes_no_btn_size[1]:
                        BTN_CLICK.play()
                        lev_exit = False
                        time_running = True
                        game_on = True

            if event.type == timer_event:
                if time_running:
                    if time != '00:00':
                        time_pass()
                    else:
                        # Opens "You lost" pop-up window
                        pygame.time.set_timer(timer_event, 0)
                        song.stop()
                        FAIL_SND.play()
                        heading = pygame.font.SysFont('impact', round(0.09375 * cur_size[1])).render(
                            'You lost!', 1, pygame.Color('#F9F9E8'))
                        heading_pos = round(0.6223 * cur_size[0] - heading.get_rect().width) // 2 + \
                                      round(0.193 * cur_size[0]), round(0.195 * cur_size[1])
                        window_pos = round(0.1889 * cur_size[0]), round(0.1823 * cur_size[1])

                        FUNCTIONAL_SURFACE.blit(popup_image, window_pos)
                        FUNCTIONAL_SURFACE.blit(heading, heading_pos)
                        lose_btns = pygame.sprite.Group()
                        los_restart = pygame.sprite.Sprite(lose_btns)
                        los_restart.image = restart_image
                        los_restart.rect = los_restart.image.get_rect()
                        los_restart.rect.x, los_restart.rect.y = round(0.39 * cur_size[0]), round(
                            0.522 * cur_size[1])

                        los_ext = pygame.sprite.Sprite(lose_btns)
                        los_ext.image = ext_image
                        los_ext.rect = los_ext.image.get_rect()
                        los_ext.rect.x, los_ext.rect.y = round(0.5124 * cur_size[0]), round(
                            0.522 * cur_size[1])
                        lose_btns.draw(FUNCTIONAL_SURFACE)

                        screen.blit(FUNCTIONAL_SURFACE, (0, 0))

                        game_on = False
                        game_over = True

            if game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    if round(0.39 * cur_size[0]) < ev_x < round(0.39 * cur_size[0]) \
                            + pause_btn_size[0] and round(0.522 * cur_size[1]) < ev_y \
                            < round(0.522 * cur_size[1]) + pause_btn_size[1]:
                        FAIL_SND.stop()
                        BTN_CLICK.play()
                        # "Restart" button restarts level
                        game_over = False
                        level_init()
                    elif round(0.5124 * cur_size[0]) < ev_x < round(0.5124 * cur_size[0]) \
                            + pause_btn_size[0] and round(0.522 * cur_size[1]) < ev_y \
                            < round(0.522 * cur_size[1]) + pause_btn_size[1]:
                        FAIL_SND.stop()
                        BTN_CLICK.play()
                        # "Exit" button returns to main menu
                        game_over = False
                        main_menu()
            elif finish:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ev_x, ev_y = event.pos
                    if round(0.39 * cur_size[0]) < ev_x < round(0.39 * cur_size[0]) \
                            + pause_btn_size[0] and round(0.522 * cur_size[1]) < ev_y \
                            < round(0.522 * cur_size[1]) + pause_btn_size[1]:
                        BTN_CLICK.play()
                        finish = False
                        next_level()  # Saving the game progress
                        level_init()  # Continuing the game
                    elif round(0.5124 * cur_size[0]) < ev_x < round(0.5124 * cur_size[0]) \
                            + pause_btn_size[0] and round(0.522 * cur_size[1]) < ev_y \
                            < round(0.522 * cur_size[1]) + pause_btn_size[1]:
                        BTN_CLICK.play()
                        finish = False
                        next_level()  # Saving the game progress
                        main_menu()  # Returning to main menu
        if game_on:
            level_blit()
            match_particle.emit()
        elif finish:
            level_blit()
            heading = pygame.font.SysFont('impact', round(0.09375 * cur_size[1])).render(
                'You won!', 1, pygame.Color('#F9F9E8'))
            heading_pos = round(0.6223 * cur_size[0] - heading.get_rect().width) // 2 + \
                          round(0.193 * cur_size[0]), round(0.195 * cur_size[1])
            window_pos = round(0.1889 * cur_size[0]), round(0.1823 * cur_size[1])

            FUNCTIONAL_SURFACE.blit(popup_image, window_pos)
            FUNCTIONAL_SURFACE.blit(heading, heading_pos)
            win_btns = pygame.sprite.Group()
            win_cont = pygame.sprite.Sprite(win_btns)
            win_cont.image = cont_image
            win_cont.rect = win_cont.image.get_rect()
            win_cont.rect.x, win_cont.rect.y = round(0.39 * cur_size[0]), round(
                0.522 * cur_size[1])

            win_ext = pygame.sprite.Sprite(win_btns)
            win_ext.image = ext_image
            win_ext.rect = win_ext.image.get_rect()
            win_ext.rect.x, win_ext.rect.y = round(0.5124 * cur_size[0]), round(
                0.522 * cur_size[1])
            win_btns.draw(FUNCTIONAL_SURFACE)

            screen.blit(FUNCTIONAL_SURFACE, (0, 0))
            win_particle.emit()
        pygame.display.flip()
        clock.tick(FPS)


def main_menu():
    # Function for main menu initialization
    global menu, menu_buttons, song
    menu = True

    # Initializing background
    menu_bcg = pygame.transform.scale(load_image('textures\\main_menu_bcg.jpg'), cur_size)
    screen.blit(menu_bcg, (0, 0))

    # Initializing logo
    logo_size = round(0.6244 * cur_size[0]), round(0.1772 * cur_size[1])
    logo_pos = round(0.1874 * cur_size[0]), round(0.0849 * cur_size[1])
    logo = pygame.transform.scale(load_image('textures\\logo.png'), logo_size)
    screen.blit(logo, logo_pos)

    # Initializing menu buttons
    menu_buttons = pygame.sprite.Group()
    menu_btn_size = round(cur_size[0] * 0.2213), round(cur_size[1] * 0.1239)

    ng = pygame.sprite.Sprite(menu_buttons)
    ng.image = pygame.transform.scale(load_image('icons\\main_new_game_btn.png'), menu_btn_size)
    ng.rect = ng.image.get_rect()
    ng.rect.x, ng.rect.y = round(0.2504 * cur_size[0]), round(0.5638 * cur_size[1])
    ng.function = 'ng'

    menu_cont = pygame.sprite.Sprite(menu_buttons)
    menu_cont.image = pygame.transform.scale(load_image('icons\\main_continue_btn.png'),
                                             menu_btn_size)
    menu_cont.rect = menu_cont.image.get_rect()
    menu_cont.rect.x, menu_cont.rect.y = round(0.5285 * cur_size[0]), round(0.5638 * cur_size[1])
    menu_cont.function = 'cont'

    hlp = pygame.sprite.Sprite(menu_buttons)
    hlp.image = pygame.transform.scale(load_image('icons\\main_help_btn.png'), menu_btn_size)
    hlp.rect = hlp.image.get_rect()
    hlp.rect.x, hlp.rect.y = round(0.1245 * cur_size[0]), round(0.7513 * cur_size[1])
    hlp.function = 'help'

    opt = pygame.sprite.Sprite(menu_buttons)
    opt.image = pygame.transform.scale(load_image('icons\\main_options_btn.png'), menu_btn_size)
    opt.rect = opt.image.get_rect()
    opt.rect.x, opt.rect.y = round(0.3894 * cur_size[0]), round(0.7513 * cur_size[1])
    opt.function = 'options'

    menu_ext = pygame.sprite.Sprite(menu_buttons)
    menu_ext.image = pygame.transform.scale(load_image('icons\\main_exit_btn.png'), menu_btn_size)
    menu_ext.rect = ng.image.get_rect()
    menu_ext.rect.x, menu_ext.rect.y = round(0.653 * cur_size[0]), round(0.7513 * cur_size[1])
    menu_ext.function = 'exit'
    menu_buttons.draw(screen)

    menu_font = pygame.font.SysFont('comic sans ms', round(0.01823 * cur_size[1]))
    coryright = menu_font.render('campfire v. 1.1 by Dream Boy, 2022', 1, pygame.Color('#F9F9E8'))
    coryright_pos = round(0.833 * cur_size[0]), round(0.97 * cur_size[1])
    screen.blit(coryright, coryright_pos)

    credits_text1 = ['BGM Credits', 'Soundtrack by Chillhop Music', 'Menu BGM:',
                     'Fenick, Delayde - Longwayhome']
    bgm_credits1 = [menu_font.render(credit, 1, pygame.Color('#F9F9E8')) for credit in credits_text1]
    x, y = round(0.004 * cur_size[0]), round(0.8919 * cur_size[1])
    dy = round(0.026 * cur_size[1])
    for line in bgm_credits1:
        screen.blit(line, (x, y))
        y += dy

    credits_text2 = ['Level BGM:', 'Psalm Trees - Rain ft. Guillaume Muschalle',
                     'Leavv - Driftwood', 'SwuM - if i leave']
    bgm_credits2 = [menu_font.render(credit, 1, pygame.Color('#F9F9E8')) for credit in credits_text2]
    x, y = round(0.1757 * cur_size[0]), round(0.8919 * cur_size[1])
    for line in bgm_credits2:
        screen.blit(line, (x, y))
        y += dy

    # Initializing main menu music
    song.stop()
    song = pygame.mixer.Sound('sounds\\songs\\menu_song.mp3')
    song.play(-1)
    song.set_volume(bgm_volume / 100)


def level_init():
    global save, menu, game_on, time_running, song, gamemode, match_particle, hint_counter, got_hint
    global lv, goal_name, goal_image, count_text, time, opened_cell, closed_cell, hint_image, coal_counter

    menu = False
    game_on = True
    time_running = True
    pygame.time.set_timer(timer_event, 1000)
    save = [line.rstrip('\n') for line in open('save_data.txt', 'r').readlines()]
    match_particle = Particle()

    # Hint button settings
    hint_counter = 0
    got_hint = False
    hint_image = hint_in_image

    # Level font
    level_font = pygame.font.SysFont('impact', round(0.05468 * cur_size[1]))

    # Cell textures
    cell_size = round(0.0563 * cur_size[0]), round(0.1 * cur_size[1])
    closed_cell = pygame.transform.scale(load_image('textures\\cell_closed.png'), cell_size)
    opened_cell = pygame.transform.scale(load_image('textures\\cell_opened.png'), cell_size)

    # Initializing game mode
    gamemode = 2 if int(save[0][7:]) % 10 == 0 else int(save[0][7:]) % 2

    # Initializing level field
    if save[1][6:] == 'None':
        n = random.randrange(12) if gamemode == 0 else random.randrange(14)
        level = open('levels/type_{}.txt'.format(str(n), 'r')).readlines()
        data = [save[0], 'type: {}'.format(str(n))] + [line for line in save[2:] if line != '']
        print(data)
        with open('save_data.txt', 'w') as savedata:
            savedata.write('\n'.join(data))
    else:
        level = open('levels/type_{}.txt'.format(save[1][6:]), 'r').readlines()
    level = [line.rstrip('\n').split() for line in level]

    # Initializing cells
    if gamemode == 0:
        cell_image = closed_cell
    else:
        cell_image = opened_cell
    cells_init(level, cell_image)

    # Initializing chips
    chip_set(level)
    if gamemode == 2:
        while coal_counter < 24:
            chip_set(level)

    # Initializing mission info
    # Level
    lv = level_font.render('Level {}'.format(save[0][7:]), 1, pygame.Color('#F9F9E8'))

    # Goal image and counter
    if gamemode == 0:
        goal_name = 'cell'
        goal = 'textures\\cell_closed.png'
        count_text = '0/{}'.format(str(cell_count))
    elif gamemode == 1:
        goal_name = random.choice(chip_names)
        goal = 'icons\\chip_{}.png'.format(goal_name)
        count_text = '0/50'
    else:
        goal_name = 'black'
        goal = 'icons\\chip_black.png'
        count_text = '0/18'
    goal_image_size = round(0.0564 * cur_size[0]), round(0.1 * cur_size[1])
    goal_image = pygame.transform.scale(load_image(goal), goal_image_size)

    # Timer
    time = '03:00'

    # Initializing level theme depending on level number
    song.stop()
    song = pygame.mixer.Sound('sounds\\songs\\level_song{}.mp3'.format(str(random.randint(1, 3))))
    song.play(-1)
    song.set_volume(bgm_volume / 100)

    # Start signal
    START_SND.play()


def cells_init(level, cell_image):
    global cell_count, cells

    # Function to initialize the field of cells
    cell_count = 0
    cells = pygame.sprite.Group()
    x0, y = round(0.33016 * cur_size[0]), round(0.08073 * cur_size[1])
    dx, dy = round(0.059297 * cur_size[0]), round(0.10547 * cur_size[1])
    for line in level:
        x = x0
        for place in line:
            if place == '1':
                cell = pygame.sprite.Sprite(cells)
                cell.image = cell_image
                cell.rect = cell.image.get_rect()
                cell.rect.x, cell.rect.y = x, y
                cell_count += 1
            x += dx
        y += dy
    cells.draw(screen)


def chip_set(level):
    global chips_list, chips, chip_names, coal_counter

    # Function to initialize the chips on field
    chips_list = []
    chips = pygame.sprite.Group()
    chip_name_list = []  # contains chip names to check repeating
    ln = 0
    x0, y = round(0.33675 * cur_size[0]), round(0.09245 * cur_size[1])
    dx, dy = round(0.059297 * cur_size[0]), round(0.10547 * cur_size[1])
    coal_counter = 0
    if gamemode == 2:
        chip_names += ['black']
    for line in level:
        x = x0
        list_line = []
        pl = 0
        for place in line:
            if coal_counter == 24:
                chip_names = chip_names[:4]
            if place == '1':
                chip_image = random.choice(chip_names)
                if pl > 1 and ln > 1:
                    cond1 = list_line[pl - 2] == chip_image
                    cond2 = list_line[pl - 1] == chip_image
                    cond3 = chip_name_list[ln - 2][pl] == chip_image
                    cond4 = chip_name_list[ln - 1][pl] == chip_image
                    while cond1 and cond2 or cond3 and cond4:
                        chip_image = random.choice(chip_names)
                        cond1 = list_line[pl - 2] == chip_image
                        cond2 = list_line[pl - 1] == chip_image
                        cond3 = chip_name_list[ln - 2][pl] == chip_image
                        cond4 = chip_name_list[ln - 1][pl] == chip_image
                elif pl > 1:
                    cond1 = list_line[pl - 2] == chip_image
                    cond2 = list_line[pl - 1] == chip_image
                    while cond1 and cond2:
                        chip_image = random.choice(chip_names)
                        cond1 = list_line[pl - 2] == chip_image
                        cond2 = list_line[pl - 1] == chip_image
                elif ln > 1:
                    cond3 = chip_name_list[ln - 2][pl] == chip_image
                    cond4 = chip_name_list[ln - 1][pl] == chip_image
                    while cond3 and cond4:
                        chip_image = random.choice(chip_names)
                        cond3 = chip_name_list[ln - 2][pl] == chip_image
                        cond4 = chip_name_list[ln - 1][pl] == chip_image
                chip = Chip(chip_image, (x, y), chips)
                if str(chip) == 'black':
                    coal_counter += 1
                list_line += [str(chip)]
                chips_list += [chip]
            else:
                list_line += [0]
            x += dx
            pl += 1
        y += dy
        chip_name_list += [list_line]
        ln += 1
    chips.draw(DISPLAY_SURFACE)


def level_blit():
    # Function to draw gameplay level
    global counter, timer

    # Level font
    level_font = pygame.font.SysFont('impact', round(0.05468 * cur_size[1]))

    # Heading
    label = level_font.render('Mission', 1, pygame.Color('#F9F9E8'))

    counter = level_font.render(count_text, 1, pygame.Color('#F9F9E8'))
    timer = level_font.render(time, 1, pygame.Color('#F9F9E8'))

    # background
    bcg = pygame.transform.scale(load_image('textures\\level_bcg.jpg'), cur_size)

    # start window
    start_box = pygame.transform.scale(load_image('textures\\game_start.png'),
                                       (round(0.365 * cur_size[0]), round(0.2978 * cur_size[1])))

    # mission screen
    mission_screen = pygame.transform.scale(load_image('textures\\mission_bcg.png'),
                                            (round(0.1469 * cur_size[0]),
                                             round(0.5478 * cur_size[1])))

    # level buttons
    level_buttons = pygame.sprite.Group()

    level_btn_size = round(0.0688 * cur_size[0]), round(0.1222 * cur_size[1])
    pause_image = pygame.transform.scale(load_image('icons\\level_pause_btn.png'), level_btn_size)
    pause = pygame.sprite.Sprite(level_buttons)
    pause.image = pause_image
    pause.rect = pause.image.get_rect()
    pause.rect.x, pause.rect.y = round(0.1219 * cur_size[0]), round(0.7956 * cur_size[1])

    hint_im = pygame.transform.scale(hint_image, level_btn_size)
    hint = pygame.sprite.Sprite(level_buttons)
    hint.image = hint_im
    hint.rect = hint.image.get_rect()
    hint.rect.x, hint.rect.y = round(0.1219 * cur_size[0]), round(0.6526 * cur_size[1])

    mission_screen_pos = round(0.0835 * cur_size[0]), round(0.0664 * cur_size[1])
    lv_pos = round(0.1537 * cur_size[0] - lv.get_rect().width) // 2 + round(
        0.0835 * cur_size[0]), round(0.1042 * cur_size[1])
    label_pos = round(0.1537 * cur_size[0] - label.get_rect().width) // 2 + round(
        0.0835 * cur_size[0]), round(0.2083 * cur_size[1])
    goal_image_pos = round(0.1537 * cur_size[0] - goal_image.get_rect().width) // 2 + round(
        0.0835 * cur_size[0]), round(0.2734 * cur_size[1])
    counter_pos = round(0.1537 * cur_size[0] - counter.get_rect().width) // 2 + round(
        0.0835 * cur_size[0]), round(0.3776 * cur_size[1])
    timer_pos = round(0.1537 * cur_size[0] - timer.get_rect().width) // 2 + round(
        0.0835 * cur_size[0]), round(0.4948 * cur_size[1])

    screen.blit(bcg, (0, 0))
    screen.blit(mission_screen, mission_screen_pos)
    level_buttons.draw(screen)
    cells.draw(screen)
    chips.draw(DISPLAY_SURFACE)
    screen.blit(lv, lv_pos)
    screen.blit(label, label_pos)
    screen.blit(goal_image, goal_image_pos)
    screen.blit(counter, counter_pos)
    screen.blit(timer, timer_pos)

    if time == '03:00':
        screen.blit(start_box, ((cur_size[0] - start_box.get_rect().width) // 2,
                                (cur_size[1] - start_box.get_rect().height) // 2))


def form_dialogue(par=None):
    bcg_pos = round(0.1889 * cur_size[0]), round(0.1823 * cur_size[1])
    yes_pos = round(0.2679 * cur_size[0]), round(0.5482 * cur_size[1])
    no_pos = round(0.511 * cur_size[0]), round(0.5482 * cur_size[1])
    done_pos = round(0.4166 * cur_size[0]), round(0.6862 * cur_size[1])
    FUNCTIONAL_SURFACE.blit(popup_image, bcg_pos)
    if par == 'yes_no':
        FUNCTIONAL_SURFACE.blit(yes_btn, yes_pos)
        FUNCTIONAL_SURFACE.blit(no_btn, no_pos)
    else:
        FUNCTIONAL_SURFACE.blit(done_btn, done_pos)


def replace(c1, c2):
    global chips_list, replaced

    replaced = c1, c2
    # Function to swap chips positions
    x1, x2 = 0, 0
    for c in range(len(chips_list)):
        if chips_list[c].sprite == c1.sprite:
            x1 = c
        elif chips_list[c].sprite == c2.sprite:
            x2 = c
    chips_list[x1], chips_list[x2] = chips_list[x2], chips_list[x1]

    c1.prep_to_swap()
    c2.prep_to_swap()

    orig1, orig2 = c1.original_coords, c2.original_coords

    c1.move(*orig2)
    c2.move(*orig1)

    c1.set_orig(orig2)
    c2.set_orig(orig1)

    level_blit()


def check_matches():
    global replaced

    deleted = False
    dx, dy = round(0.0593 * cur_size[0]), round(0.10546 * cur_size[1])
    for chip in chips_list:
        hor_chips, ver_chips = [], []
        to_delete = []
        for near_chip in chips_list:
            if near_chip.sprite.rect != chip.sprite.rect:
                # Checking by y axis
                if near_chip.original_coords[0] == chip.original_coords[0]:
                    if near_chip.original_coords[1] == chip.original_coords[1] + dy:
                        if near_chip == chip:
                            ver_chips += [near_chip]
                    elif len(ver_chips) == 1:
                        if near_chip.original_coords[1] == chip.original_coords[1] + dy * 2:
                            if near_chip == chip:
                                ver_chips += [near_chip]
                    elif len(ver_chips) == 2:
                        if near_chip.original_coords[1] == chip.original_coords[1] + dy * 3:
                            if near_chip == chip:
                                ver_chips += [near_chip]
                    elif len(ver_chips) == 3:
                        if near_chip.original_coords[1] == chip.original_coords[1] + dy * 4:
                            if near_chip == chip:
                                ver_chips += [near_chip]

                # Checking by x axis
                elif near_chip.original_coords[1] == chip.original_coords[1]:
                    if near_chip.original_coords[0] == chip.original_coords[0] + dx:
                        if near_chip == chip:
                            hor_chips += [near_chip]
                    elif len(hor_chips) == 1:
                        if near_chip.original_coords[0] == chip.original_coords[0] + dx * 2:
                            if near_chip == chip:
                                hor_chips += [near_chip]
                    elif len(hor_chips) == 2:
                        if near_chip.original_coords[0] == chip.original_coords[0] + dx * 3:
                            if near_chip == chip:
                                hor_chips += [near_chip]
                    elif len(hor_chips) == 3:
                        if near_chip.original_coords[0] == chip.original_coords[0] + dx * 4:
                            if near_chip == chip:
                                hor_chips += [near_chip]

        if len(hor_chips) > 1:
            to_delete += hor_chips
        if len(ver_chips) > 1:
            to_delete += ver_chips
        if to_delete:
            to_delete += [chip]
            if len(to_delete) >= 4:
                hint_acquire()
            delete_chips(to_delete)
            deleted = True
            replaced = False
    if not deleted and replaced:
        RETURN_SND.play()
        replace(*replaced)
        replaced = None


def delete_chips(to_delete):
    global chips_list, cells, chips, match_particle
    deleted = []
    MATCH_SND.play()
    dy_coeff = 0.01166 if cur_size != (1280, 720) else 0.01181
    dx, dy = round(0.00659 * cur_size[0]), round(dy_coeff * cur_size[1])
    for chip in to_delete:
        if chip.sprite not in deleted:
            deleted += [chip.sprite]
            if goal_name == str(chip):
                mission_progress(1)
    for chip in deleted:
        coords = chip.rect.x, chip.rect.y
        new = Chip(random.choice(chip_names), coords, chips)
        if gamemode == 0:
            for cell in cells:
                if (cell.rect.x + dx, cell.rect.y + dy) == (chip.rect.x, chip.rect.y) \
                        and cell.image != opened_cell:
                    cell.image = opened_cell
                    mission_progress(1)
                    break
        for c in range(len(chips_list)):
            if chips_list[c].sprite == chip:
                chips_list[c] = new
                break
        match_particle.add_particles(chip.rect.x, chip.rect.y, chip.rect.width)
        chip.kill()


def mission_progress(val):
    global count_text

    MISSION_SND.play()

    count_text = str(int(count_text[:count_text.find('/')]) + val) \
                 + count_text[count_text.find('/'):]


def newgame():
    global new_game, save
    with open('save_data.txt', 'r') as savedata:
        sd = savedata.readlines()[2:]
    with open('save_data.txt', 'w') as savedata:
        data = 'level: 1\ntype: None\n' + ''.join(sd)
        savedata.write(data)
    save = [line.rstrip('\n') for line in open('save_data.txt', 'r').readlines()]
    new_game = False
    level_init()


def time_pass():
    global time

    if time[3:] == '00':
        time = '0' + str(int(time[1]) - 1) + ':59'
    else:
        minutes = str(int(time[3:]) - 1)
        while len(minutes) != 2:
            minutes = '0' + minutes
        time = time[:3] + minutes


def hint_acquire():
    global hint_counter, got_hint, hint_image

    HINT_SND.play()
    hint_counter += 1
    if hint_counter == 3:
        hint_image = hint_act_image
        got_hint = True


def hint():
    global got_hint, hint_image, hint_counter

    BTN_CLICK.play()
    got_hint = False
    hint_image = hint_in_image
    hint_counter = 0

    random_chip_id = random.randrange(len(chips_list))
    to_delete = chips_list[random_chip_id - 3:random_chip_id]
    delete_chips(to_delete)


def next_level():
    global save
    with open('save_data.txt', 'r') as sd:
        savedata = sd.readlines()
        level = int(savedata[0][7:]) + 1
        opt = savedata[2:]
    with open('save_data.txt', 'w') as sd:
        to_write = 'level: {}\ntype: None\n{}'.format(str(level), ''.join(opt))
        sd.write(to_write)
    save = [line.rstrip('\n') for line in open('save_data.txt', 'r').readlines()]


def options_form():
    form_dialogue()
    heading = pygame.font.SysFont('impact', round(0.09375 * cur_size[1])).render(
        'Options', 1, pygame.Color('#F9F9E8'))
    heading_pos = round(0.6222 * cur_size[0] - heading.get_rect().width
                        ) // 2 + 0.1925 * cur_size[0], round(0.1953 * cur_size[1])

    popup_font = pygame.font.SysFont('impact', round(0.0625 * cur_size[1]))
    bgm_lbl = popup_font.render('Music volume', 1, pygame.Color('#F9F9E8'))
    snd_lbl = popup_font.render('Sound volume', 1, pygame.Color('#F9F9E8'))
    fullscr_lbl = popup_font.render('Fullscreen mode', 1, pygame.Color('#F9F9E8'))

    bgm_lbl_pos = round(0.2703 * cur_size[0]), round(0.357 * cur_size[1])
    snd_lbl_pos = round(0.2703 * cur_size[0]), round(0.482 * cur_size[1])
    fullscr_lbl_pos = round(0.275 * cur_size[0]) + checkbox_size[0], round(0.6 * cur_size[1])
    checkbox_pos = round(0.2703 * cur_size[0]), round(0.612 * cur_size[1])
    checkbox = fs_checkbox_ch if fullscreen else fs_checkbox_un
    FUNCTIONAL_SURFACE.blit(heading, heading_pos)
    FUNCTIONAL_SURFACE.blit(bgm_lbl, bgm_lbl_pos)
    FUNCTIONAL_SURFACE.blit(snd_lbl, snd_lbl_pos)
    FUNCTIONAL_SURFACE.blit(checkbox, checkbox_pos)
    FUNCTIONAL_SURFACE.blit(fullscr_lbl, fullscr_lbl_pos)

    screen.blit(FUNCTIONAL_SURFACE, (0, 0))


def fullscreen_set():
    global fullscreen, screen

    fullscreen = not fullscreen
    with open('save_data.txt', 'r') as sd:
        savedata = sd.readlines()[:4]
    with open('save_data.txt', 'w') as sd:
        to_write = ''.join(savedata) + 'fullscreen: {}'.format('1' if fullscreen else '0')
        sd.write(to_write)

    pygame.display.quit()
    window_pos = (0, 0) if fullscreen else (117, 66)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % window_pos
    pygame.display.init()
    screen_setting()
    main_menu()


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    game()