import pygame as pg
import cv2

from consultation.screen import Screen, BlitLocation, Colours, Fonts
from consultation_lightweight import User, ConsultConfig
from consultation.display_screen import DisplayScreen
from consultation.touch_screen import TouchScreen
from consultation.avatar import Avatar
from consultation.perceived_stress_score import PSS


class Consultation:
    def __init__(self, user=None, enable_speech=True):

        if user:
            self.user = user
        else:
            # create demo user
            self.user = User("Demo", 65)

        self.config = ConsultConfig(speech=enable_speech)

        self.display_size = pg.Vector2(1024, 600)

        # load all attributes which utilise any pygame surfaces!

        self.window = pg.display.set_mode((self.display_size.x, self.display_size.y * 2), pg.SRCALPHA)
        self.top_screen = self.window.subsurface(((0, 0), self.display_size))
        self.bottom_screen = self.window.subsurface((0, self.display_size.y), self.display_size)

        self.fonts = Fonts()
        self.display_screen = DisplayScreen(self.top_screen.get_size())
        self.touch_screen = TouchScreen(self.bottom_screen.get_size())

        self.avatar = Avatar(size=(256, 256 * 1.125))

        self.modules = [PSS(self, question_count=1)]
        self.module_idx = 0

        self.running = True

        self.update_display()

    def update_display(self):
        self.touch_screen.screen.refresh()
        self.display_screen.update()
        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()

    def get_relative_mose_pos(self):
        return pg.Vector2(pg.mouse.get_pos()) - pg.Vector2(0, self.display_size.y)

    def take_screenshot(self):
        print("Taking Screenshot")
        img_array = pg.surfarray.array3d(self.parent.window)
        img_array = cv2.transpose(img_array)
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        cv2.imwrite("screenshot.png", img_array)

    def loop(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        module = self.modules[self.module_idx]
                        module.running = True
                        print("Entering PSS Loop")
                        module.loop()
                        self.update_display()
                        print("Leaving PSS Loop")

                    elif event.key == pg.K_x:
                        self.touch_screen.show_sprites = not self.touch_screen.show_sprites
                        self.update_display()

                # elif event.type == pg.MOUSEBUTTONDOWN:
                #     button_id = self.touch_screen.click_test(self.get_relative_mose_pos())

                elif event.type == pg.QUIT:
                    self.running = False


if __name__ == "__main__":
    pg.init()
    consult = Consultation()
    consult.loop()


