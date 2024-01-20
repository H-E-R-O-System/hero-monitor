import pygame as pg
from consultation.screen import Screen, BlitLocation, Colours, Fonts
from consultation.avatar import Avatar
from consultation.questions import Question
import os
import math


class AvatarBackground:
    def __init__(self, size):
        self.screen = Screen(size, colour=Colours.white.value)
        self.avatar = Avatar(size=(256, 288))
        self.state = 0
        self.time = 12
        self.sun = pg.image.load("consultation/graphics/Sun.png")
        self.moon = pg.image.load("consultation/graphics/Moon.png")

        self.sun = pg.transform.scale(self.sun, (80, 80))
        self.moon = pg.transform.scale(self.moon, (80, 80))

    def update(self):
        def get_position(time):
            x = 1.5 - time / 12
            if 6 <= time <= 18:
                y = 1.2-(math.sqrt(math.pow(0.5, 2) - math.pow((x - 0.5), 2))/0.5)
            else:
                y = -100

            return x * self.screen.size.x, y * self.screen.size.y * 0.8

        if self.state == 0:
            self.screen.surface.fill(Colours.white.value)
        else:
            self.screen.refresh()
            if 5 > self.time or self.time >= 20:
                colour = pg.Color("#5C4E63")
            elif 8 <= self.time < 17:
                colour = pg.Color("#45b3e0")
            else:
                colour = pg.Color("#E3785E")

            colour.a = 200

            self.screen.surface.fill(colour)
            if 6 <= self.time <= 18:
                self.screen.add_image(self.sun, get_position(self.time), location=BlitLocation.centre)

            if self.time <= 6 or self.time >= 18:
                self.screen.add_image(self.moon, get_position((self.time + 12) % 24), location=BlitLocation.centre)

    def get_surface(self):
        return self.screen.surface


class DisplayScreen:
    def __init__(self, size):
        size = pg.Vector2(size)
        fonts = Fonts()
        self.screen = Screen(size, colour=Colours.white.value)

        self.text_screen_info = Screen((size.x, size.y * 0.2),
                                       font=fonts.normal, colour=Colours.midGrey.value)

        self.avatar_display = AvatarBackground((size.x, size.y - self.text_screen_info.size.y))
        self.avatar_display.update()

        self.text_screen_main = Screen((size.x * 0.6,
                                       size.y - self.text_screen_info.size.y),
                                       fonts.normal, colour=Colours.lightGrey.value)

        self.avatar = Avatar(size=(256, 288))
        self.avatar.state = 0
        self.instruction = "Press Q to start"

    def update(self, question=None):
        self.text_screen_info.refresh()
        self.text_screen_main.refresh()
        self.avatar_display.update()
        self.screen.refresh()

        if self.instruction:
            self.text_screen_info.add_text(self.instruction, pos=self.text_screen_info.size / 2,
                                           location=BlitLocation.centre)

        if question:
            avatar_pos = (self.avatar_display.screen.size.x / 5, self.avatar_display.screen.size.y / 2)
        else:
            avatar_pos = (self.avatar_display.screen.size.x / 2, self.avatar_display.screen.size.y / 2)

        self.avatar_display.screen.add_surf(self.avatar.get_surface(), pos=avatar_pos, location=BlitLocation.centre)

        self.screen.add_surf(self.text_screen_info.get_surface(), (0, self.screen.size.y), location=BlitLocation.bottomLeft)
        self.screen.add_surf(self.avatar_display.get_surface(), (0, 0))

        if question:
            # self.text_screen_main.add_text(question.text, (20, 20))
            self.text_screen_main.add_multiline_text(question.text, (20, 20))
            for idx, hint in enumerate(question.hints):
                self.text_screen_main.add_text("• " + hint, (40, 70 + 50*idx))

            self.screen.add_surf(self.text_screen_main.get_surface(), pos=(self.screen.size.x, 0), location=BlitLocation.topRight)

    def get_surface(self):
        return self.screen.get_surface()


if __name__ == "__main__":
    os.chdir('/Users/benhoskings/Documents/Projects/hero-monitor')
    pg.init()
    window = pg.display.set_mode(pg.Vector2(1024, 600))
    consult_display = DisplayScreen(pg.Vector2(window.get_size()))
    consult_display.avatar_display.state = 1
    # consult_display.avatar.state = 2
    consult_display.update()
    # consult_display.avatar.state = 1
    # consult_display.avatar.speak_state = 1

    window.blit(consult_display.get_surface(), (0, 0))
    pg.display.update()

    q1 = "How are you feeling today?"
    h1 = ["has today been overall positive or negative",
          "has you felt any physical pain"]

    question_1 = Question(q1, h1)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    consult_display.avatar_display.state = 0
                    consult_display.instruction = "Press F to end answer"
                    consult_display.update(question_1)
                elif event.key == pg.K_f:
                    consult_display.avatar_display.state = 1
                    consult_display.instruction = "Press Q to ask question"
                    consult_display.update()

                elif event.key == pg.K_1:
                    consult_display.avatar_display.time = (consult_display.avatar_display.time + 1) % 24
                    print(consult_display.avatar_display.time)
                    consult_display.update()

                window.blit(consult_display.get_surface(), (0, 0))
                pg.display.update()
