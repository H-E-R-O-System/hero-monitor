import pygame as pg

from consultation.screen import Screen, BlitLocation, Colours


class GameButton(pg.sprite.Sprite):
    def __init__(self, position, size, id, text=None, label=None, colour=None):
        super().__init__()
        self.object_type = "button"
        self.rect = pg.Rect(position, size)
        self.id = id
        if colour:
            self.colour = colour.value
        else:
            self.colour = Colours.hero_blue.value
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
                if obj.text:
                    screen.add_text(obj.text, colour=Colours.white, location=BlitLocation.centre, pos=obj.rect.center,
                                    sprite=True)
                if obj.label:
                    screen.add_text(obj.label, colour=Colours.darkGrey, location=BlitLocation.midBottom, pos=obj.rect.midtop,
                                    sprite=True)

            elif obj.object_type == "card" or obj.object_type == "circle":
                screen.add_surf(obj.image, pos=obj.rect.topleft, sprite=True)

            elif obj.object_type == "clock_hand":
                screen.add_surf(obj.image, screen.size / 2, location=BlitLocation.centre, sprite=True)


class TouchScreen(Screen):
    def __init__(self, size, colour=Colours.white):
        super().__init__(size, colour=colour)
        self.sprites = GameObjects([])
        self.power_off = False

        self.power_off_surface = pg.Surface((self.size.x, self.size.y), pg.SRCALPHA)
        self.power_off_surface.fill(Colours.white.value)

        # self.touch_screen.surface.fill(Colours.white.value)
        # self.display_screen.state = 2
        #
        # self.touch_screen.load_image("consultation/graphics/logo.png", size=self.touch_screen.size.yy * 0.8,
        #                              pos=self.touch_screen.size / 2, location=BlitLocation.centre)
        image = pg.image.load("consultation/graphics/logo.png")
        image = pg.transform.scale(image, size=self.size.yy * 0.8)
        pos = self.size / 2

        imageRect = pg.Rect(pos, image.get_size())
        imageRect.topleft = pg.Vector2(imageRect.topleft) - pg.Vector2(imageRect.size) / 2

        self.power_off_surface.blit(image, imageRect)

    def click_test(self, pos):
        if self.sprites:
            for sprite in self.sprites:
                if sprite.is_clicked(pos):
                    return sprite.click_return()

        return None

    def kill_sprites(self):
        self.sprites.empty()

    def get_surface(self):
        if self.power_off:
            return self.power_off_surface

        self.sprites.draw(self)
        display_surf = self.base_surface.copy()
        display_surf.blit(self.surface, (0, 0))
        display_surf.blit(self.sprite_surface, (0, 0))

        return display_surf

    def get_object(self, object_id):
        for game_object in self.sprites:
            if game_object.id == object_id:
                return game_object

