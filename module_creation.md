# Creating a module for the consultation

## Modular design
### Each module should be constructed as a class with the following template.

    class MouleName:
        def __init__(self):
            self.running = False
            # Additional class properties
        
        def entry_sequence(self):
            # Everything needed to intrododuce your module 
            ...
        
        def exit_sequence(self):
            # Short thank you for completeing the section
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