# Creating a module for the consultation

## Modular design
### Each module should be constructed as a class with the following template in the file **`module_name.py`**

```python
import pygame as pg


class ModuleName:
    def __init__(self):
        self.running = False
        # Additional class properties
    
    def entry_sequence(self):
        # pre-loop initialisation section
        # Everything needed to introduce your module
        # OPTIONAL and can leave blank
        ...
    
    def exit_sequence(self):
        # post-loop completion section
        # maybe add Short thank you for completing the section?
        # OPTIONAL and can leave blank
        ...

    def loop(self):
        self.entry_sequence()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        # do something with key press
                        ...

                elif event.type == pg.MOUSEBUTTONDOWN:
                    # do something with mouse click
                    mouse_pos = pg.mouse.get_pos()
                    ...

                elif event.type == pg.QUIT:
                    # break the running loop
                    self.running = False

        self.exit_sequence()
```
    