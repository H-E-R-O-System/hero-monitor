import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

class recolourImage():
    def __init__(self):
        self.colourPaletter = []
        self.base_colours = []
        # self.base_colour = [14, 80, 250]
        self.new_colour = [14, 80, 200]
        self.img_colour_palette = []
        self.tol = 69

    def getImage(self, image_path):
        self.img = cv2.imread(image_path)

    def dispColourPalette(self, colour_palette):
        num_colours = len(colour_palette)
        # print(num_colours)
        # Display the colour palette
        plt.figure()
        cols = 20
        rows = math.ceil(num_colours/cols)
        for idx, col in enumerate(colour_palette):
            plt.subplot(rows, cols, idx+1)
            # convert to rgb
            colour =  cv2.cvtColor(np.uint8([[col]]), cv2.COLOR_BGR2RGB)[0, 0, :]
            plt.imshow([[colour]], extent=(0, 1, 0, 1))

            # if skin tone add a rectangle
            if list(col) in self.base_colours:
                rect = patches.Rectangle((0, 0), 1, 1, linewidth=3, edgecolor='b', facecolor='none')
                plt.gca().add_patch(rect)
            elif col in [item for sublist in self.img_colour_palette for item in sublist]:
                rect = patches.Rectangle((0, 0), 1, 1, linewidth=3, edgecolor='r', facecolor='none')
                plt.gca().add_patch(rect)

            plt.title(idx, fontsize=7)
            plt.axis('off')
    
    def showImg(self):
        # show image
        plt.figure()
        plt.imshow(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
        plt.axis('off')
    
    def getColourPalette(self):
        self.colour_palette = set(tuple(pixel) for row in self.img for pixel in row)
    
    def colourDistance(self, color1, color2):
        return np.linalg.norm(np.array(color1) - np.array(color2))
    
    def getBaseColours(self):
        self.img_colour_palette = []
        for idx, base in enumerate(self.base_colours):
            self.img_colour_palette.append([]) # empty list
            for col in self.colour_palette:
                # self.colour_distance(col,col)
                if self.colourDistance(base,col) < self.tol:
                    self.img_colour_palette[idx].append(col)

    def dispChange(self):
        plt.figure()
        plt.subplot(1, 2, 1)
        colour =  cv2.cvtColor(np.uint8([[self.base_colours[0]]]), cv2.COLOR_BGR2RGB)[0, 0, :]
        plt.imshow([[colour]], extent=(0, 1, 0, 1))
        plt.axis('off')
        plt.subplot(1, 2, 2)
        colour =  cv2.cvtColor(np.uint8([[self.new_colour]]), cv2.COLOR_BGR2RGB)[0, 0, :]
        plt.imshow([[colour]], extent=(0, 1, 0, 1))
        plt.axis('off')

    def changeColuring(self):
        self.getColourPalette()
        self.getBaseColours()

        for idx, col in enumerate(self.colour_palette):
            for base_idx, cols in enumerate(self.img_colour_palette):
                if col in self.img_colour_palette[base_idx]:
                    mask = np.all(self.img == col, axis=-1)

                    ni = self.new_colour - (np.array(self.base_colours[0]) - np.array(self.base_colours[base_idx]))
                    # Generate the new skin colour
                    update = np.array(self.base_colours[base_idx]) - np.array(col)
                    new_col = ni - update

                    # if base_idx > 0:
                    #     print(base_idx)
                    #     print(self.base_colours)
                    #     new_col -= np.array(self.base_colours[0]) - np.array(self.base_colours[base_idx])

                    # colour = cv2.cvtColor(np.uint8([[new_col]]), cv2.COLOR_HSV2BGR)[0, 0, :]
                    self.img[mask] = new_col
    
    def baseSelector(self):
        self.fig, self.ax = plt.subplots()
        self.ax.imshow(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
        self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onHover)
        self.fig.canvas.mpl_connect('key_press_event', self.onKeyPress)
        self.ax.set_title(f'Tolerance: {self.tol:.2f}')
        plt.show()
        
    def onClick(self, event):
        if event.xdata is not None and event.ydata is not None:
            x, y = int(event.xdata), int(event.ydata)
            selected_color = self.img[y, x]
            print(f"Selected Color: {selected_color}")
            self.base_colours.append(list(selected_color))
            # plt.close()  # Close the image window after selecting the color

    def onHover(self, event):
        if event.xdata is not None and event.ydata is not None:
            print(self.base_colours)
            x, y = int(event.xdata), int(event.ydata)
            self.base_colours.append(list(self.img[y, x]))

            # highlight area affected
            self.getColourPalette()
            self.getBaseColours()
            
            disp_img = np.copy(self.img)

            for idx, col in enumerate(self.colour_palette):
                for base_palette in self.img_colour_palette:
                    if col in base_palette:
                        mask = np.all(self.img == np.array(col), axis=-1)
                        # Generate the new skin colour
                        new_col = 0.5*np.array(col)
                        disp_img[mask] = new_col
            # self.ax.clear()
            # self.ax.imshow(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
            self.ax.imshow(cv2.cvtColor(disp_img, cv2.COLOR_BGR2RGB))
            self.ax.set_title(f'Tolerance: {self.tol:.2f}')
            plt.draw()
            # remove the temp colour from the list
            self.base_colours.pop()
    
    def onKeyPress(self, event):
        if event.key == '=':
            self.tol += 1
        elif event.key == '-':
            self.tol -= 1
        elif event.key == ']':
            self.tol *= 1.25
        elif event.key == '[':
            self.tol /= 1.25
        elif event.key == 'r':
            # reset
            self.base_colours = []
        elif event.key == 'c':
            plt.close()  # Close the image window after selecting the color
        self.onHover(event)


if __name__ == "__main__":
    # baseImg = "Male103"
    baseImg = "Female103"
    # baseImg = "image7"
    # baseImg = "image4"


    r = recolourImage()
    r.tol = 158

    # select the base colour to change
    r.getImage(f"{baseImg}.png")
    r.baseSelector()

    # show the changes that will happen to all images
    # r.getImage(f"{baseImg}.png")
    # r.getColourPalette()
    # r.getBaseColours()
    # r.dispColourPalette(r.colour_palette)

    # Changing skintones

    # NEED TO COMMENT BACK ON
    r.getImage("skinColours2.png")
    r.getColourPalette()
    colours = r.colour_palette

    # calc size of figure
    plt.figure()
    cols = 5
    rows = math.ceil(len(colours)/cols)
    for idx, col in enumerate(colours):
        # make a new character
        r.new_colour = col
        # get the image to replace
        r.getImage(f"{baseImg}.png")
        r.changeColuring()
        # r.dispColourPalette(r.colour_palette)
        # plt.figure()
        plt.subplot(rows, cols, idx+1)
        plt.imshow(cv2.cvtColor(r.img, cv2.COLOR_BGR2RGB))
        plt.axis('off')

        # save the image into a png
        cv2.imwrite(f"skintones/{baseImg}_sc{idx}.png", r.img)
    
    plt.show()
