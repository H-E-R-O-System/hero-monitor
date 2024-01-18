# Creating a module for the consultation

## Modular design
### Each module should be constructed as a class with the following template in the file **`module_name.py`**

```python
import pygame as pg
from consultation.touch_screen import TouchScreen
from consultation.display_screen import DisplayScreen
from consultation.screen import Colours

class ModuleName:
    def __init__(self, size=(1024, 600), parent=None):
        if parent is not None:
            self.display_size = parent.display_size
            self.bottom_screen = parent.bottom_screen
            self.top_screen = parent.top_screen
        else:
            self.display_size = pg.Vector2(size)
            self.bottom_screen = pg.display.set_mode(self.display_size)
            self.top_screen = pg.display.set_mode(self.display_size) # can set to None if not required

        self.display_screen = DisplayScreen(self.display_size)
        self.touch_screen = TouchScreen(self.display_size)
        
        # Additional class properties
        self.thing1 = None
        self.thing2 = None
        
        # initialise module
        self.update_display()
        self.running = True
        
    def update_display(self):
        self.top_screen.blit(self.display_screen.get_surface(), (0, 0))
        self.bottom_screen.blit(self.touch_screen.get_surface(), (0, 0))
        pg.display.flip()
    
    def entry_sequence(self):
        # pre-loop initialisation section
        # add everything needed to introduce your module and explain
        # what the users are expected to do (e.g. game rules, aim, etc.)
        
        # only OPTIONAL and can leave blank
        ...
    
    def do_something(self, ):
        # Do something useful
        ...
    
    def exit_sequence(self):
        # post-loop completion section
        # maybe add short thank you for completing the section?
        
        # only OPTIONAL and can leave blank
        ...
    

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        # do something with key press
                        ...
                    elif event.key == pg.K_ESCAPE:
                        self.running = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    # do something with mouse click
                    mouse_pos = pg.mouse.get_pos()
                    ...

                elif event.type == pg.QUIT:
                    # break the running loop
                    self.running = False

        self.exit_sequence()


if __name__ == "__main__":
    # Module Testing
    module_name = ModuleName()
    module_name.loop()
    print("Module run successfully")
```
    