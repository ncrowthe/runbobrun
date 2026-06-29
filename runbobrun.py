from tkinter import *
from tkinter import messagebox
import random
import time
from typing import Any

MAX_TIME_SECS = 60

class Coords:
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

def within_x(co1, co2):
    if (co1.x1 > co2.x1 and co1.x1 < co2.x2) \
            or (co1.x2 > co2.x1 and co1.x2 < co2.x2) \
            or (co2.x1 > co1.x1 and co2.x1 < co1.x2) \
            or (co2.x2 > co1.x1 and co2.x2 < co1.x2):
        return True
    else:
        return False

def within_y(co1, co2):
    if (co1.y1 > co2.y1 and co1.y1 < co2.y2) \
            or (co1.y2 > co2.y1 and co1.y2 < co2.y2) \
            or (co2.y1 > co1.y1 and co2.y1 < co1.y2) \
            or (co2.y2 > co1.y1 and co2.y2 < co1.y2):
        return True
    else:
        return False

def collided_left(co1, co2):
    if within_y(co1, co2):
        if co1.x1 >= co2.x1 and co1.x1 <= co2.x2:
            return True
    return False

def collided_right(co1, co2):
    if within_y(co1, co2):
        if co1.x2 >= co2.x1 and co1.x2 <= co2.x2:
            return True
    return False

def collided_top(co1, co2):
    if within_x(co1, co2):
        if co1.y1 >= co2.y1 and co1.y1 <= co2.y2:
            return False
    return False

def collided_bottom(y, co1, co2):
    if within_x(co1, co2):
        y_calc = co1.y2 + y
        if y_calc >= co2.y1 and y_calc <= co2.y2:
            return True
    return False

class Sprite:
    def __init__(self, game):
        self.game = game
        self.endgame = False
        self.coordinates = None
    def move(self):
        pass
    def coords(self):
        return self.coordinates

class PlatformSprite(Sprite):
    def __init__(self, game, photo_image1, photo_image2, x, y, width, height):
        Sprite.__init__(self, game)

        self.game = game
        self.last_time = time.time()
        self.current_image = 1
        self.x = x
        self.y = y
        self.photo_image1 = photo_image1
        self.photo_image2 = photo_image2        
        self.image = game.canvas.create_image(x, y,
                image=photo_image1, anchor='nw')
        self.coordinates = Coords(x, y, x + width, y + height)

    def move(self):
        if time.time() - self.last_time > 0.2:
            self.last_time = time.time()
            self.current_image = 2 if self.current_image == 1 else 1
        image = self.photo_image1 if self.current_image == 1 else self.photo_image2
        self.game.canvas.itemconfig(self.image, image=image)


class StickFigureSprite(Sprite):
    def __init__(self, game):
        Sprite.__init__(self, game)
        self.images_left = [
            PhotoImage(file='icons/figure-L1.gif'),
            PhotoImage(file='icons/figure-L2.gif'),
            PhotoImage(file='icons/figure-L3.gif')
        ]
        self.images_right = [
            PhotoImage(file='icons/figure-L1.gif'),
            PhotoImage(file='icons/figure-L2.gif'),
            PhotoImage(file='icons/figure-L3.gif')
        ]
        self.figure_wet = PhotoImage(file='icons/figure-wet.gif')
        self.image = game.canvas.create_image(200, 470,
                image=self.images_left[0], anchor='nw')
        self.x = -2
        self.y = 0
        self.current_image = 0
        self.current_image_add = 1
        self.jump_count = 0
        self.last_time = time.time()
        self.coordinates = Coords()
        game.canvas.bind_all('<KeyPress-Left>', self.turn_left)
        game.canvas.bind_all('<KeyPress-Right>', self.turn_right)
        game.canvas.bind_all('<space>', self.jump)

    def turn_left(self, evt):
        if self.y == 0:
            self.x = -2

    def turn_right(self, evt):
        if self.y == 0:
            self.x = 2

    def jump(self, evt):
        if self.y == 0:
            self.y = -4
            self.jump_count = 0

    def animate(self):
        if self.x != 0 and self.y == 0:
            if time.time() - self.last_time > 0.1:
                self.last_time = time.time()
                self.current_image += self.current_image_add
                if self.current_image >= 2:
                    self.current_image_add = -1
                if self.current_image <= 0:
                    self.current_image_add = 1
        if self.x < 0:
            if self.y != 0:
                self.game.canvas.itemconfig(self.image, 
                        image=self.images_left[2])
            else:
                self.game.canvas.itemconfig(self.image, 
                        image=self.images_left[self.current_image])
        elif self.x > 0:
            if self.y != 0:
                self.game.canvas.itemconfig(self.image, 
                        image=self.images_right[2])
            else:
                self.game.canvas.itemconfig(self.image, 
                        image=self.images_right[self.current_image])

    def coords(self):
        xy = self.game.canvas.coords(self.image)
        self.coordinates.x1 = xy[0]
        self.coordinates.y1 = xy[1]
        self.coordinates.x2 = xy[0] + 27
        self.coordinates.y2 = xy[1] + 30
        return self.coordinates

    def move(self):
        self.animate()
        if self.y < 0:
            self.jump_count += 1
            if self.jump_count > 20:
                self.y = 4
        if self.y > 0:
            self.jump_count -= 1
        co = self.coords()
        left = True
        right = True
        top = True
        bottom = True
        falling = True
        if self.y > 0 and co.y2 >= self.game.canvas_height:
            self.y = 0
            bottom = False
        elif self.y < 0 and co.y1 <= 0:
            self.y = 0
            top = False
        if self.x > 0 and co.x2 >= self.game.canvas_width:
            self.x = 0
            right = False
        elif self.x < 0 and co.x1 <= 0:
            self.x = 0
            left = False

        for sprite in self.game.sprites:
            if sprite == self:
                continue
            sprite_co = sprite.coords()
            if top and self.y < 0 and collided_top(co, sprite_co):
                self.y = -self.y
                top = False
                if sprite.endgame:
                    if isinstance(sprite, ToiletSprite):
                        self.game.end_code = self.game.COMPLETED
                        ## move to next level
                    elif isinstance(sprite, MonsterSprite):
                        self.game.end_code = self.game.EATEN
                    self.game.running = False
            if bottom and self.y > 0 and collided_bottom(self.y, 
                    co, sprite_co):
                self.y = sprite_co.y1 - co.y2
                if self.y < 0:
                    self.y = 0
                bottom = False
                top = False
                if sprite.endgame:
                    if isinstance(sprite, ToiletSprite):
                        self.game.end_code = self.game.COMPLETED
                    elif isinstance(sprite, MonsterSprite):
                        self.game.end_code = self.game.EATEN
                    self.game.running = False
            if bottom and falling and self.y == 0 \
                    and co.y2 < self.game.canvas_height \
                    and collided_bottom(1, co, sprite_co):
                falling = False
            if left and self.x < 0 and collided_left(co, sprite_co):
                self.x = 0
                left = False
                if sprite.endgame:
                    if isinstance(sprite, ToiletSprite):
                        self.game.end_code = self.game.COMPLETED
                    elif isinstance(sprite, MonsterSprite):
                        self.game.end_code = self.game.EATEN
                    self.game.running = False
            if right and self.x > 0 and collided_right(co, sprite_co):
                self.x = 0
                right = False
                if sprite.endgame:
                    if isinstance(sprite, ToiletSprite):
                        self.game.end_code = self.game.COMPLETED
                    elif isinstance(sprite, MonsterSprite):
                        self.game.end_code = self.game.EATEN
                    self.game.running = False

        if falling and bottom and self.y == 0 \
                and co.y2 < self.game.canvas_height:
            self.y = 4
        self.game.canvas.move(self.image, self.x, self.y)

class ToiletSprite(Sprite):
    def __init__(self, game, photo_image, image_wet, x, y, y_movement, width, height):
        Sprite.__init__(self, game)
        self.photo_image = photo_image
        self.image_wet = image_wet
        self.y_movement = y_movement
        self.image = game.canvas.create_image(x, y, 
                image=self.photo_image, anchor='nw')
        self.coordinates = Coords(x, y, x + (width / 2), y + height)
        self.y_delta = 1
        self.y_count = 0
        self.endgame = True        

    def move(self):
        if self.y_count >= self.y_movement:
            self.y_delta = -1
        elif self.y_count <= 0:
            self.y_delta = 1
        self.y_count += self.y_delta
        self.game.canvas.move(self.image, 0, self.y_delta)
        self.coordinates.y1 += self.y_delta
        self.coordinates.y2 += self.y_delta

class MonsterSprite(Sprite):
    def __init__(self, game, photo_image, x, y, x_movement, y_movement, width, height):
        Sprite.__init__(self, game)
        self.photo_image = photo_image
        self.x_movement = x_movement        
        self.y_movement = y_movement
        self.image = game.canvas.create_image(x, y, 
                image=self.photo_image, anchor='nw')
        self.coordinates = Coords(x, y, x + (width / 2), y + height)

        self.x_delta = 1
        self.x_count = 0

        self.y_delta = 1
        self.y_count = 0        

        self.endgame = True

    def move(self):
        if self.y_count >= self.y_movement:
            self.y_delta = -2
        elif self.y_count <= 0:
            self.y_delta = 2
        self.y_count += self.y_delta

        if self.x_count >= self.x_movement:
            self.x_delta = -2
        elif self.x_count <= 0:
            self.x_delta = 2
        self.x_count += self.x_delta

        self.game.canvas.move(self.image, self.x_delta, self.y_delta)

        self.coordinates.x1 += self.x_delta
        self.coordinates.x2 += self.x_delta     

        self.coordinates.y1 += self.y_delta
        self.coordinates.y2 += self.y_delta            

class Game:

    TIME_OUT = 1
    EATEN = 2
    COMPLETED = 3

    def __init__(self):
        self.level = 1
        self.tk = Tk()
        self.tk.title('Run Bob Run')
        self.tk.resizable(0, 0)
        self.tk.wm_attributes('-topmost', 1)
        self.canvas = Canvas(self.tk, width=500, height=500, 
                             highlightthickness=0)
        self.canvas.pack()
        self.tk.update()
        self.canvas_height = self.canvas.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
    
    def play(self)  :
        elapsed = time.time() - self.start_time
        remaining = max(0, MAX_TIME_SECS - int(elapsed))
        self.canvas.itemconfig(self.timer_text, text=str(remaining))
        if elapsed > MAX_TIME_SECS:
            self.running = False
            self.end_code = self.TIME_OUT
        for sprite in self.sprites:
            sprite.move()

    def gameOver(self):
        for sprite in self.sprites:
            if isinstance(sprite, ToiletSprite):
                self.canvas.itemconfig(sprite.image,
                        image=sprite.image_wet)

            if isinstance(sprite, StickFigureSprite):
                self.canvas.itemconfig(sprite.image,
                        image=sprite.figure_wet)

            self.tk.update_idletasks()
            self.tk.update()                                

        if (self.end_code == self.COMPLETED):
            self.canvas.create_text(250, 380, text="Well Done!",
                    font=('Helvetica', 30), fill='blue')

        if (self.end_code == self.EATEN):
            self.canvas.create_text(250, 380, text="You've been eaten!",
                    font=('Helvetica', 30), fill='red')

        if (self.end_code == self.TIME_OUT):
            self.canvas.create_text(250, 380, text="Time out!",
                    font=('Helvetica', 30), fill='red')                                        


        self.tk.update_idletasks()
        self.tk.update()
        time.sleep(3)

    def mainloop(self):
        while True:
            if self.running == True:
                self.play()
            else:
                self.gameOver()

                self.newGame(   (self.end_code == self.COMPLETED))
                break
            self.tk.update_idletasks()
            self.tk.update()
            time.sleep(0.02)

    def newGame(self, incrementLevel):

        self.sprites = []
        self.end_code = self.COMPLETED
        self.running = True
        self.start_time = time.time()

        if (incrementLevel):
            self.level = self.level + 1

        self.tk.title('Run Bob Run Level ' + str(self.level))

        self.bg = PhotoImage(file='icons/background.gif')
        w = self.bg.width()
        h = self.bg.height()
        for x in range(0, 5):
            for y in range(0, 5):
                self.canvas.create_image(x * w, y * h, 
                        image=self.bg, anchor='nw')
        self.sprites = []
        self.end_code = self.COMPLETED
        self.timer_text = self.canvas.create_text(490, 10,
            text=str(MAX_TIME_SECS), font=('Helvetica', 18), fill='white', anchor='ne')        

        p1a =  PhotoImage(file='icons/platform1a.gif')
        p1b =  PhotoImage(file='icons/platform1b.gif')
        p2a =  PhotoImage(file='icons/platform2a.gif')
        p2b =  PhotoImage(file='icons/platform2b.gif')
        p3a =  PhotoImage(file='icons/platform3a.gif')
        p3b =  PhotoImage(file='icons/platform3b.gif')

        MAX_RIGHT = 12
        #, game, photo_image1, photo_image2, x, y, width, height
        platform10 = PlatformSprite(game=self, photo_image1=p2a, photo_image2=p2b, x = 45, y=60, width=60, height=10)
        platform9 = PlatformSprite(self, p2a, p2b,  100, 120, 60, 10)                           
        platform8 = PlatformSprite(self, p3a, p3b,  200 , 160, 32, 10)
        platform7 = PlatformSprite(self, p2a, p2b, 260 , 200, 60, 10)
        platform6 = PlatformSprite(self, p2a, p2b, 170 , 250, 60, 10)        
        platform5 = PlatformSprite(self, p1a, p1b, 50 , 300, 100, 10)   
        platform4 = PlatformSprite(self, p1a, p1b, 175 , 350, 100, 10)  
        platform3 = PlatformSprite(self, p2a, p2b, 300 , 400, 60, 10)                               
        platform2 = PlatformSprite(self, p1a, p1b, 150 , 440, 100, 10)                                                
        platform1 = PlatformSprite(self, p2a, p2b, 30 , 480, 60, 10)                                                                       
        self.sprites.append(platform1)
        self.sprites.append(platform2)
        self.sprites.append(platform3)
        self.sprites.append(platform4)
        self.sprites.append(platform5)
        self.sprites.append(platform6)
        self.sprites.append(platform7)
        self.sprites.append(platform8)
        self.sprites.append(platform9)
        self.sprites.append(platform10)

        toilet: ToiletSprite = ToiletSprite(self, PhotoImage(file='icons/toilet-empty.gif'), PhotoImage(file='icons/toilet-fill.gif'), 8, 30,  80, 27, 30)
        self.sprites.append(toilet)

        if (self.level > 1):
            monster: MonsterSprite = MonsterSprite(self, PhotoImage(file='icons/monster1a.gif'), 20,    200, 30, 320, 30, 35)
            self.sprites.append(monster)

        if (self.level > 2):
            monster2: MonsterSprite = MonsterSprite(self, PhotoImage(file='icons/monster1a.gif'), 30,   80, 90, 380, 30, 35)
            self.sprites.append(monster2)        

        if (self.level > 3):
            monster3: MonsterSprite = MonsterSprite(self, PhotoImage(file='icons/monster1a.gif'), 40,  200, 180, 300, 30, 35)
            self.sprites.append(monster3)     

        if (self.level > 4):
            monster4: MonsterSprite = MonsterSprite(self, PhotoImage(file='icons/monster1a.gif'), 60, 240, 120, 320, 30, 35)
            self.sprites.append(monster4)                           

        sf = StickFigureSprite(self)
        self.sprites.append(sf)
        self.mainloop()

g = Game()
g.newGame(True)        