from tkinter import *
from tkinter import messagebox
import random
import time
from tkinter import PhotoImage
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

def collided_top(co1: Coords, co2: Coords) -> bool:
    return within_x(co1, co2) and co2.y1 <= co1.y1 <= co2.y2    

def collided_bottom(y, co1, co2):
    if within_x(co1, co2):
        y_calc = co1.y2 + y
        if y_calc >= co2.y1 and y_calc <= co2.y2:
            return True
    return False

class Sprite:

    SPRITE_HEIGHT = 30
    SPRITE_WIDTH = 27

    def __init__(self, game):
        self.game = game
        self.endgame = False
        self.coordinates = None
    def move(self):
        pass
    def coords(self):
        return self.coordinates

class PlatformSprite(Sprite):
    def __init__(self, game, photo_image1, photo_image2, x, y, width, height, y_movement=0):
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

        self.y_movement = y_movement
        self.y_delta = 1
        self.y_count = 0

    def move(self):
        if time.time() - self.last_time > 0.2:
            self.last_time = time.time()
            self.current_image = 2 if self.current_image == 1 else 1
        image = self.photo_image1 if self.current_image == 1 else self.photo_image2
        self.game.canvas.itemconfig(self.image, image=image)

        if self.y_movement:
            if self.y_count >= self.y_movement:
                self.y_delta = -1
            elif self.y_count <= 0:
                self.y_delta = 1
            self.y_count += self.y_delta
            self.game.canvas.move(self.image, 0, self.y_delta)
            self.coordinates.y1 += self.y_delta
            self.coordinates.y2 += self.y_delta


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
        self.figure_fail= PhotoImage(file='icons/figure-fail.gif')
        self.image = game.canvas.create_image(0, 470,
                image=self.images_left[0], anchor='nw')
        self.x = 0
        self.y = 0
        self.current_image = 0
        self.current_image_add = 1
        self.jump_count = 0
        self.jump_max = 20
        self.last_time = time.time()
        self.coordinates = Coords()
        game.canvas.bind_all('<KeyPress-Left>', self.turn_left)
        game.canvas.bind_all('<KeyPress-Right>', self.turn_right)
        game.canvas.bind_all('<space>', self.jump)

    def turn_left(self, evt):
            self.x = -2

    def turn_right(self, evt):
            self.x = 2

    def jump(self, evt):
        if self.y == 0:
            self.jump_max = 40 if evt.state & 0x4 else 20
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
        self.coordinates.x2 = xy[0] + self.SPRITE_WIDTH
        self.coordinates.y2 = xy[1] + self.SPRITE_HEIGHT
        return self.coordinates

    def checkSpriteAction(self, sprite):
        if sprite.endgame:
            if isinstance(sprite, BinSprite):
                self.game.end_code = self.game.COMPLETED
                ## move to next level
            elif isinstance(sprite, MonsterSprite):
                self.game.end_code = self.game.EATEN
            self.game.running = False
        else:
            if isinstance(sprite, PointSprite):
                self.game.points += sprite.points
                self.y = self.y + 5
                self.game.canvas.delete(sprite.image)
                try:
                    self.game.sprites.remove(sprite)
                except ValueError:
                    pass

    def move(self):
        self.animate()
        if self.y < 0:
            self.jump_count += 1
            if self.jump_count > self.jump_max:
                self.y = 2
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

            if (isinstance(sprite, PointSprite) 
            and top and self.y < 0 and collided_top(co, sprite_co)):
                self.y = -self.y
                top = False
                self.checkSpriteAction(sprite)

            if bottom and self.y > 0 and collided_bottom(self.y, 
                    co, sprite_co):
                self.y = sprite_co.y1 - co.y2
                if self.y < 0:
                    self.y = 0
                bottom = False
                top = False
                self.checkSpriteAction(sprite)
                
            if bottom and falling and self.y == 0 \
                    and co.y2 < self.game.canvas_height \
                    and collided_bottom(1, co, sprite_co):
                falling = False
                if sprite.y_movement and sprite.y_delta < 0:
                    self.game.canvas.move(self.image, 0, sprite.y_delta)

            if left and self.x < 0 and collided_left(co, sprite_co):
                self.x = 0
                left = False
                self.checkSpriteAction(sprite)

            if right and self.x > 0 and collided_right(co, sprite_co):
                self.x = 0
                right = False
                self.checkSpriteAction(sprite)

        if falling and bottom and self.y == 0 \
                and co.y2 < self.game.canvas_height:
            self.y = 4

        self.game.canvas.move(self.image, self.x, self.y)

class PointSprite(Sprite):
    def __init__(self, game, image_open, image_closed, x, y, y_movement, width, height):
        Sprite.__init__(self, game)
        self.last_time = time.time()
        self.current_image = 1        
        self.image_open = image_open
        self.image_closed = image_closed
        self.y_movement = y_movement
        self.image = game.canvas.create_image(x, y, 
                image=self.image_open, anchor='nw')
        self.coordinates = Coords(x, y, x + (width / 2), y + height)
        self.y_delta = 1
        self.y_count = 0
        self.points = 10
        self.endgame = False        

    def move(self):
        if self.y_count >= self.y_movement:
            self.y_delta = -1
        elif self.y_count <= 0:
            self.y_delta = 1
        self.y_count += self.y_delta
        self.game.canvas.move(self.image, 0, self.y_delta)
        self.coordinates.y1 += self.y_delta
        self.coordinates.y2 += self.y_delta

        # Alternate pics
        if time.time() - self.last_time > 0.2:
            self.last_time = time.time()
            self.current_image = 2 if self.current_image == 1 else 1
        image = self.image_open if self.current_image == 1 else self.image_closed
        self.game.canvas.itemconfig(self.image, image=image)            

class ToiletSprite(PointSprite):
    pass    

class BananaSprite(PointSprite):
    def __init__(self, game, image_open, image_closed, x, y, y_movement, width, height):
        PointSprite.__init__(self, game, image_open, image_closed, x, y, y_movement, width, height)
        self.points = 40       

class SodaSprite(PointSprite):
    def __init__(self, game, image_open, image_closed, x, y, y_movement, width, height):
        PointSprite.__init__(self, game, image_open, image_closed, x, y, y_movement, width, height)
        self.points = 20       

class BinSprite(PointSprite):
    def __init__(self, game, image_open, image_closed, x, y, y_movement, width, height):
        PointSprite.__init__(self, game, image_open, image_closed, x, y, y_movement, width, height)
        self.points = 50  
        self.endgame = True   

class PooSprite(PointSprite):
    def __init__(self, game, image_open, image_closed, x, y, y_movement, width, height):
        PointSprite.__init__(self, game, image_open, image_closed, x, y, y_movement, width, height)
        self.points = -20           
         
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

        self.points = -100
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
        self.level = 0
        self.points = 0
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
        self.canvas.itemconfig(self.points_text, text=str(self.points))
        if elapsed > MAX_TIME_SECS:
            self.running = False
            self.end_code = self.TIME_OUT
        for sprite in self.sprites:
            sprite.move()

    def gameOver(self):
        for sprite in self.sprites:
            if isinstance(sprite, StickFigureSprite):
                if (self.end_code != self.COMPLETED):
                    self.canvas.itemconfig(sprite.image,
                            image=sprite.figure_fail)

            self.tk.update_idletasks()
            self.tk.update()                                

        if (self.end_code == self.COMPLETED):
            self.canvas.create_rectangle(150, 350, 350, 410, fill='black', outline='green')               
            self.canvas.create_text(250, 380, text="Well Done!",
                    font=('Helvetica', 30), fill='green')

        if (self.end_code == self.EATEN):
            self.canvas.create_rectangle(170, 360, 330, 400, fill='black', outline='red')            
            self.canvas.create_text(250, 380, text="Eaten!",
                    font=('Helvetica', 30), fill='red')

        if (self.end_code == self.TIME_OUT):
            self.canvas.create_rectangle(160, 360, 340, 400, fill='black', outline='red')            
            self.canvas.create_text(250, 380, text="Time Out!",
                    font=('Helvetica', 30), fill='red')                              


        self.tk.update_idletasks()
        self.tk.update()
        time.sleep(3)

    def mainloop(self):
        while True:
            if self.running:
                self.play()
            else:
                self.gameOver()

                #self.newGame(  True)
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

        self.tk.title('Binman Bob Level ' + str(self.level))

        self.bg = PhotoImage(file='icons/background.gif')
        w = self.bg.width()
        h = self.bg.height()
        for x in range(0, 5):
            for y in range(0, 5):
                self.canvas.create_image(x * w, y * h, 
                        image=self.bg, anchor='nw')

        self.canvas.create_rectangle(458, 4, 498, 40, fill='black', outline='white')
        self.timer_text = self.canvas.create_text(490, 10,
            text=str(MAX_TIME_SECS), font=('Helvetica', 18), fill='white', anchor='ne')
        self.canvas.create_rectangle(400, 4, 448, 40, fill='black', outline='white')
        self.points_text = self.canvas.create_text(406, 10,
            text=str(self.points), font=('Helvetica', 18), fill='white', anchor='nw')

        p1a =  PhotoImage(file='icons/platform1a.gif')
        p1b =  PhotoImage(file='icons/platform1b.gif')
        p2a =  PhotoImage(file='icons/platform2a.gif')
        p2b =  PhotoImage(file='icons/platform2b.gif')
        p3a =  PhotoImage(file='icons/platform3a.gif')
        p3b =  PhotoImage(file='icons/platform3b.gif')

        MAX_RIGHT = 12
        #, game, photo_image1, photo_image2, x, y, width, height
        if (self.level == 0):
            platform10 = PlatformSprite(game=self, photo_image1=p3a, photo_image2=p3b, x = 45, y=60, width=32, height=10, y_movement=10)
            self.sprites.append(platform10)

        platform9 = PlatformSprite(self, p2a, p2b,  100, 120, 66, 10)                           
        platform8 = PlatformSprite(self, p3a, p3b,  200 , 160, 32, 10)
        platform7 = PlatformSprite(self, p2a, p2b, 260 , 200, 66, 10)
        platform6 = PlatformSprite(self, p3a, p3b, 170 , 250, 32, 10)        
        platform5 = PlatformSprite(self, p1a, p1b, 150 , 300, 100, 10)   
        platform4 = PlatformSprite(self, p3a, p3b, 300 , 350, 32, 10)  
        platform3 = PlatformSprite(self, p2a, p2b, 380 , 400, 66, 10)                               
        platform2 = PlatformSprite(self, p1a, p1b, 250 , 440, 100, 10)                                                
        platform1 = PlatformSprite(self, p2a, p2b, 180 , 480, 66, 10)                                                                       
        self.sprites.append(platform1)
        self.sprites.append(platform2)
        self.sprites.append(platform3)
        self.sprites.append(platform4)
        self.sprites.append(platform5)
        self.sprites.append(platform6)
        self.sprites.append(platform7)
        self.sprites.append(platform8)
        self.sprites.append(platform9)

        #self, game, photo_image, x, y, x_movement, y_movement, width, height
        monster: MonsterSprite = MonsterSprite(self, PhotoImage(file='icons/monster1a.gif'), 20,    200, 300, 320, 30, 35)
        self.sprites.append(monster)

        if (self.level > 1):
            monster2: MonsterSprite = MonsterSprite(self, PhotoImage(file='icons/monster1a.gif'), 30,   80, 90, 380, 30, 35)
            self.sprites.append(monster2)        

        if (self.level > 2):
            monster3: MonsterSprite = MonsterSprite(self, PhotoImage(file='icons/monster1a.gif'), 80,  200, 180, 300, 30, 35)
            self.sprites.append(monster3)     

        if (self.level > 3):
            monster4: MonsterSprite = MonsterSprite(self, PhotoImage(file='icons/monster1a.gif'), 160, 240, 120, 320, 30, 35)
            self.sprites.append(monster4)  

        if (self.level > 4):
            monster5: MonsterSprite = MonsterSprite(self, PhotoImage(file='icons/monster1a.gif'), 260, 30, 160, 300, 30, 35)
            self.sprites.append(monster5)             

        img_open   = PhotoImage(file='icons/toilet-open.gif')
        img_closed = PhotoImage(file='icons/toilet-closed.gif')

        if (self.level > 0):
            toilet = ToiletSprite(self, image_open=img_open, image_closed=img_closed, x=2, y=40,  y_movement=200, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
            self.sprites.append(toilet) 
        if (self.level >=4):
            toilet  = ToiletSprite(self, image_open=img_open, image_closed=img_closed, x=300, y=0,  y_movement=80, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
            self.sprites.append(toilet)     

        bananaImg1: PhotoImage   = PhotoImage(file='icons/banana1.gif')
        bananaImg2: PhotoImage   = PhotoImage(file='icons/banana1.gif')
        banana1 = BananaSprite(self, image_open=bananaImg1, image_closed=bananaImg2, x=random.randint(0, 460), y=random.randint(0, 200),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(banana1)
        banana2 = BananaSprite(self, image_open=bananaImg1, image_closed=bananaImg2, x=random.randint(0, 460), y=random.randint(0, 200),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(banana2)
        banana3 = BananaSprite(self, image_open=bananaImg1, image_closed=bananaImg2, x=random.randint(0, 460), y=random.randint(0, 200),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(banana3)
        banana4 = BananaSprite(self, image_open=bananaImg1, image_closed=bananaImg2, x=random.randint(0, 460), y=random.randint(0, 200),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(banana4)     

        sodaImg1: PhotoImage   = PhotoImage(file='icons/soda-can.gif')
        sodaImg2: PhotoImage   = PhotoImage(file='icons/soda-can.gif')
        soda1: SodaSprite = SodaSprite(self, image_open=sodaImg1, image_closed=sodaImg2, x=random.randint(0, 460), y=random.randint(240, 460),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(soda1)
        soda2 = SodaSprite(self, image_open=sodaImg1, image_closed=sodaImg2, x=random.randint(0, 460), y=random.randint(240, 460),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(soda2)
        soda3 = SodaSprite(self, image_open=sodaImg1, image_closed=sodaImg2, x=random.randint(0, 460), y=random.randint(240, 460),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(soda3)
        soda4 = SodaSprite(self, image_open=sodaImg1, image_closed=sodaImg2, x=random.randint(0, 460), y=random.randint(240, 460),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(soda4)      

        pooImg1: PhotoImage   = PhotoImage(file='icons/poo.gif')
        pooImg2: PhotoImage   = PhotoImage(file='icons/poo.gif')
        poo1 = PooSprite(self, image_open=pooImg1, image_closed=pooImg2, x=random.randint(0, 460), y=random.randint(0, 460),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(poo1)
        poo2 = PooSprite(self, image_open=pooImg1, image_closed=pooImg2, x=random.randint(0, 460), y=random.randint(0, 460),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(poo2)
        poo3 = PooSprite(self, image_open=pooImg1, image_closed=pooImg2, x=random.randint(0, 460), y=random.randint(0, 460),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(poo3)
        poo4 = PooSprite(self, image_open=pooImg1, image_closed=pooImg2, x=random.randint(0, 460), y=random.randint(0, 460),  y_movement=4, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(poo4)           

        bin_open   = PhotoImage(file='icons/bin-open.gif')
        bin_closed = PhotoImage(file='icons/bin-closed.gif')
        bin = BinSprite(self, image_open=bin_open, image_closed=bin_closed, x=2, y=20,  y_movement=1, width=Sprite.SPRITE_WIDTH, height=Sprite.SPRITE_HEIGHT)
        self.sprites.append(bin) 

        sf = StickFigureSprite(self)
        self.sprites.append(sf)

        self.mainloop()

g = Game()
g.newGame(False)        