from consultation.screen import Screen, BlitLocation, Colours
import pygame as pg


class GameButton(pg.sprite.Sprite):
    def __init__(self, position, size, id, text=None, label=None):
        super().__init__()
        self.object_type = "button"
        self.rect = pg.Rect(position, size)
        self.id = id
        self.colour = Colours.darkGrey.value
        self.text = text
        self.label = label

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False

    def click_return(self):
        return self.id


class GameObjects(pg.sprite.Group):
    def __init__(self, sprites):
        super().__init__(self, sprites)

    def draw(self, screen: Screen, bgsurf=None, special_flags: int = 0):
        for obj in self.sprites():
            if obj.object_type == "button":
                pg.draw.rect(screen.sprite_surface, obj.colour, obj.rect, border_radius=16)
                if obj.label:
                    screen.add_text(obj.text, colour=Colours.white, location=BlitLocation.centre, pos=obj.rect.center,
                                    sprite=True)
                    screen.add_text(obj.label, colour=Colours.darkGrey, location=BlitLocation.midBottom, pos=obj.rect.midtop,
                                    sprite=True)

            elif obj.object_type == "card":
                screen.add_surf(obj.image, pos=obj.rect.topleft, sprite=True)


class TouchScreen:
    def __init__(self, size):
        self.screen = Screen(size, colour=Colours.white.value)
        self.screen.refresh()

        self.sprites = GameObjects([])
        self.show_sprites = False

    def click_test(self, pos):
        if self.sprites:
            for sprite in self.sprites:
                if sprite.is_clicked(pos):
                    return sprite.click_return()

        return None

    def load_likert_buttons(self, height, count=5):
        buttons = []
        gap = 10
        labels = ["Never", "Almost Never", "Sometimes", "Very Often", "Always"]
        for idx in range(count):
            width = (self.screen.size.x - (count + 1) * gap) / count
            position = gap + idx * ((self.screen.size.x - (count + 1) * gap) / count + gap)
            button = GameButton(pg.Vector2(position, height), pg.Vector2(width, 50), idx, text=str(idx), label=labels[idx])
            buttons.append(button)

        self.sprites = GameObjects(buttons)
        self.sprites.draw(self.screen)
        self.show_sprites = True

    def kill_sprites(self):
        self.sprites.empty()
        self.sprites.draw(self.screen)

    def refresh(self):
        self.screen.refresh()

    def get_surface(self):
        self.sprites.draw(self.screen)
        return self.screen.get_surface(self.show_sprites)
