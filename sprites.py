import pygame as pg
import os
from typing import Any, Tuple, Sequence
from scipy.constants import speed_of_light, Planck, elementary_charge, pi
from random import randint
from math import sqrt, cos

pg.font.init()

main_dir = os.path.split(os.path.abspath(__file__))[0]
img_dir = os.path.join(main_dir, 'img')
font_dir = os.path.join(main_dir, 'fonts')
font_linlibertine_b = os.path.join(font_dir, 'LinLibertine_RB.ttf')
font_roboto = os.path.join(font_dir, 'Roboto-Regular.ttf')
electron_mass = 9.1e-31

spectrum = pg.Surface((471, 5))
violet = pg.Surface((100, 5))
violet.fill((127, 0, 255))
violet_rect = violet.get_rect()
spectrum.blit(violet, violet_rect)
visible_path = os.path.join(img_dir, "visible_spectrum.png")
visible = pg.image.load(visible_path)
visible = pg.transform.scale(visible, (371, 5))
visible_rect = visible.get_rect(topleft=(100, 0))
spectrum.blit(visible, visible_rect)

font_label = pg.font.Font(font_linlibertine_b, 23)
font_button = pg.font.Font(font_roboto, 20)
font_slider = pg.font.Font(font_roboto, 15)

class Electron(pg.sprite.Sprite):
    image = pg.image.load(os.path.join(img_dir, "electron.png"))
    image = pg.transform.scale(image, (10, 10))
    def __init__(self, velocity: float, space: pg.Rect) -> None:
        super().__init__()

        self.velocity = velocity
        self.space = space

        start_coords = 234, randint(121, 211)
        self.rect = self.image.get_rect(topleft=start_coords)

        self.delta_x = 0

    def update(self, timedelta, voltage: float) -> None:
        self.delta_x += self.velocity*timedelta
        if int(self.delta_x):
            self.rect.move_ip(self.delta_x, 0)
            self.delta_x -= int(self.delta_x)

        if self.rect.colliderect(self.space):
            e_field_strength = voltage / 0.1
            electric_force = e_field_strength * elementary_charge
            acceleration = electric_force / electron_mass
            self.velocity += (acceleration*timedelta)
        else:
            self.kill()
        return 

class Photocell(pg.sprite.Sprite):
    work_function_of_materials = {  # in aJ
        "Al": 0.68,
        "Au": 0.77,
        "As": 0.82,
        "Ba": 0.42,
        "Be": 0.71,
        "Cs": 0.31,
        "Ce": 0.46,
        "Eu": 0.4,
        "Ag": 0.69,
        "Ga": 0.66,
        "Ge": 0.78,
        "Hf": 0.62,
        "Ca": 0.45,
        "K": 0.36,
        "Hg": 0.72,
        "Pb": 0.66,
    }

    max_wavelength_of_materials = {
        "Al": 290,
        "Au": 260,
        "As": 245,
        "Ba": 480,
        "Be": 280,
        "Cs": 635,
        "Ce": 435,
        "Eu": 500,
        "Ag": 290,
        "Ga": 300,
        "Ge": 255,
        "Hf": 320,
        "Ca": 440,
        "K": 550,
        "Hg": 275,
        "Pb": 300,
    }

    photocell_img = pg.image.load(os.path.join(img_dir, 'photocell.png'))
    photocell_rect = photocell_img.get_rect()
    photocell_left_img = pg.image.load(os.path.join(img_dir, 'photocell_left.png'))
    photocell_left_rect = photocell_left_img.get_rect()

    def __init__(self, light_performance: int = 2.5e19, wave_length: int = 515, voltage: float = 5.05e-3, catode_mat: str = "Al") -> None:
        super().__init__()        

        self.catode_mat = catode_mat
        self.refresh_catode()
        
        self.light_performance = light_performance
        self.wave_length = wave_length
        self.voltage = voltage
        self.current = 0
        self.electron_count = 0

        self.image = pg.Surface((1000, 450))
        self.rect = self.image.get_rect()
        
        self.render_photocell()

    def update(self, timedelta: float, *args: Any, **kwargs: Any) -> None:
        if self.wave_length < self.max_wavelength:
            energy_per_photon = Planck * (speed_of_light / (self.wave_length*1e-9))
            electron_count = (self.light_performance * timedelta) // 1
            kinetic_energy_per_electron = energy_per_photon - self.work_function*1e-18
        else:
            electron_count = 0

        self.current = (electron_count * elementary_charge) / timedelta
        self.electron_count += electron_count

        electrons = []
        electrons_to_display = int(self.electron_count/5e14)
        for i in range(electrons_to_display):
            velocity = sqrt((2 * kinetic_energy_per_electron) / electron_mass)
            degree = randint(0, 85)
            radian = (degree/360) * 2*pi
            velocity_x = velocity * cos(radian)

            electron = Electron(velocity_x, self.space_between_electrodes)
            electrons.append(electron)

            self.electron_count -= 5e14

        return electrons

    def render_current(self):
        # w: 110, h: 45
        widget = pg.Surface((114, 49))
        widget.fill((0, 0, 0))
        widget.set_clip(pg.Rect(2, 2, 110, 45))
        widget.fill((255, 255, 255))
        widget_r = widget.get_rect()

        current_to_render = round(self.current, 2)
        text = font_label.render(f"I = {current_to_render} A", True, (0, 0, 0))
        textpos = text.get_rect(center=widget_r.center)

        widget_r.move_ip(440, 305)

        widget.blit(text, textpos)
        self.image.blit(widget, widget_r)

    def render_voltage(self):
        widget = pg.Surface((134, 49))
        widget.fill((0, 0, 0))
        widget.set_clip(pg.Rect(2, 2, 130, 45))
        widget.fill((255, 255, 255))
        widget_r = widget.get_rect()

        voltage_to_render = self.voltage * 1000
        text = font_label.render(f"U = {voltage_to_render} mV", True, (0, 0, 0))
        textpos = text.get_rect(center=widget_r.center)

        widget_r.move_ip(150, 305)

        widget.blit(text, textpos)
        self.image.blit(widget, widget_r)
        
    def render_photocell(self):
        self.image = pg.Surface((1000, 450))
        self.rect = self.image.get_rect()

        # space between electrodes
        # 233, 121 -- topleft
        # 740, 218 -- bottomright
        self.space_between_electrodes = pg.Rect(233, 121, 497, 100)

        color_coord = (self.wave_length - 280, 1)
        lightray_color = spectrum.get_at(color_coord)[:3]
        lightray_transparency = int((self.light_performance / 5e19) * 255)
        lightray = pg.Surface((330, 45), pg.SRCALPHA)
        lightray.fill((*lightray_color, lightray_transparency))
        self.lightray = pg.transform.rotate(lightray, 21)
        self.lightray_rect = self.lightray.get_rect(center=(368, 116))

        self.image.blit(self.photocell_img, self.photocell_rect)
        self.image.blit(self.lightray, self.lightray_rect)
        self.image.blit(self.photocell_left_img, self.photocell_left_rect)

    def refresh_catode(self):
        self.work_function = self.work_function_of_materials[self.catode_mat]
        self.max_wavelength = self.max_wavelength_of_materials[self.catode_mat]

class MenuButton(pg.sprite.Sprite):
    def __init__(self, parent: pg.sprite.Sprite, name: str, txt: str):
        super().__init__()

        self.parent = parent
        self.image = pg.Surface((200, 60))
        self.image.fill((0, 0, 0))
        self.image.set_clip(pg.Rect(2, 2, 196, 56))
        self.rect = self.image.get_rect()

        self.name = name
        self.text = font_button.render(txt, True, (0, 0, 0))
        self.textpos = self.text.get_rect(center=self.rect.center)

        self.render_inactive()
        
    def render_inactive(self):
        self.rect = self.image.get_rect()
        self.image.fill((255, 255, 255))
        self.image.blit(self.text, self.textpos)

    def render_active(self):
        self.rect = self.image.get_rect()
        self.image.fill((200, 200, 255))
        self.image.blit(self.text, self.textpos)

    # def point_inside(self, coords: Tuple[int]):
    #     x = coords[0] - self.parent.rect.topleft[0]
    #     y = coords[1] - self.parent.rect.topleft[1]
    #     return self.rect.collidepoint((x, y))


class Menu(pg.sprite.Sprite):
    def __init__(self, image: pg.Surface, topleft: Tuple[int] = (0, 0), *buttons) -> None:
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(topleft=topleft)

        self.buttons = pg.sprite.Group(buttons)
        if buttons:
            self.active = buttons[0]
            self.active.render_active()
        else:
            self.active = MenuButton(self, 'temp', ' ')

        self.arrange()
        
    def arrange(self):
        if self.buttons:
            x = int((self.image.get_width() / 2) // 1)
            row_h = int((self.image.get_height() / (len(self.buttons) + 1)) // 1)

            for i, widget in enumerate(self.buttons):
                i += 1
                widget.rect.center = x, row_h * i
                self.image.blit(widget.image, widget.rect)

    def change_active(self, to: MenuButton):
        self.active.render_inactive()
        to.render_active()
        self.active = to

        self.arrange()

    def clicked(self, pos: Tuple[int]):
        for b in self.buttons:
            if b.rect.collidepoint(pos):
                self.change_active(b)


class Slider(pg.sprite.Sprite):
    cursor_path = os.path.join(img_dir, 'slider_cursor.png')
    cursor_img = pg.image.load(cursor_path)
    cursor_img = pg.transform.scale(cursor_img, (8, 64))

    def __init__(self, scale_img: pg.Surface, min_value: float, max_value: float, unit: str, accuracy: int = 0) -> None:
        super().__init__()

        self.image = pg.Surface((500, 100))
        self.rect = self.image.get_rect()
        
        self.scale_w = 350
        self.scale_img = pg.transform.scale(scale_img, (self.scale_w, 50))
        self.scale_vert_center = self.rect.centery + 15
        self.scale_rect = self.scale_img.get_rect(center=(self.rect.centerx, self.scale_vert_center))

        self.min_value = min_value
        self.max_value = max_value
        self.interval = max_value - min_value
        self.actual_value = self.min_value + self.interval/2
        self.unit = unit
        
        self.accuracy = accuracy

        self.display_init(mousepos=self.scale_rect.center)

        self.ongoing_input = False
        self.mouse_start = None
        self.mouse_interval = (self.scale_rect.left + 4, self.scale_rect.right - 4)

    def display_init(self, mousepos: Tuple[int]):
        limit_display_w = 75
        limit_display_h = 60

        self.min_display_img = pg.Surface((limit_display_w, limit_display_h))
        self.min_display_img.fill((255, 255, 255))
        self.min_display_rect = self.min_display_img.get_rect(center=(int(limit_display_w/2), self.scale_rect.centery))
        text = font_slider.render(f"{self.min_value} {self.unit}", True, (0, 0, 0))
        textpos = text.get_rect(center=self.min_display_img.get_rect().center)
        self.min_display_img.blit(text, textpos)

        self.max_display_img = pg.Surface((limit_display_w, limit_display_h))
        self.max_display_img.fill((255, 255, 255))
        self.max_display_rect = self.max_display_img.get_rect(center=(int(limit_display_w/2) + limit_display_w + self.scale_rect.width, self.scale_rect.centery))
        text = font_slider.render(f"{self.max_value} {self.unit}", True, (0, 0, 0))
        textpos = text.get_rect(center=self.max_display_img.get_rect().center)
        self.max_display_img.blit(text, textpos)

        self.render_pos(mousepos=mousepos)

    def render_pos(self, mousepos: Tuple[int]):
        self.image.fill((255, 255, 255))

        actual_display_h = 40
        self.actual_display_img = pg.Surface((60, actual_display_h))
        self.actual_display_img.fill((255, 255, 255))
        self.actual_display_rect = self.actual_display_img.get_rect(center=(self.image.get_rect().centerx, actual_display_h/2))    
        text = font_slider.render(f"{self.actual_value} {self.unit}", True, (0, 0, 0))
        textpos = text.get_rect(center=self.actual_display_img.get_rect().center)
        self.actual_display_img.blit(text, textpos)

        self.cursor_rect = self.cursor_img.get_rect(center=mousepos)

        self.image.blit(self.scale_img, self.scale_rect)
        self.image.blit(self.min_display_img, self.min_display_rect)
        self.image.blit(self.max_display_img, self.max_display_rect)
        self.image.blit(self.actual_display_img, self.actual_display_rect)
        self.image.blit(self.cursor_img, self.cursor_rect)

    def handle_input(self, pos: Tuple[int], type: str):
        pos_x = pos[0] - self.rect.topleft[0]
        pos_y = pos[1] - self.rect.topleft[1]
        pos = pos_x, pos_y
        
        if self.cursor_rect.collidepoint(pos) and type == "start":
            self.ongoing_input = True
            self.mouse_start = pos
        elif self.ongoing_input:
            deltax = pos_x - self.mouse_start[0]

            mouse_newx = self.mouse_start[0] + deltax
            if mouse_newx < self.mouse_interval[0]:
                mouse_newx = self.mouse_interval[0]
            elif mouse_newx > self.mouse_interval[1]:
                mouse_newx = self.mouse_interval[1]

            x_rel = mouse_newx - self.mouse_interval[0]
            position_percentage = x_rel / (self.mouse_interval[1] - self.mouse_interval[0])
            new_value = self.min_value + self.interval*position_percentage

            if self.accuracy == 0:
                self.actual_value = int(round(new_value, 0))
            else:
                self.actual_value = round(new_value, self.accuracy)

            self.render_pos(mousepos=(mouse_newx, self.scale_vert_center))

            if type == "stop":
                self.ongoing_input = False
                return self.actual_value

        return False


class LightSettings(pg.sprite.Sprite):
    name = "light"
    def __init__(self, parent: pg.sprite.Sprite, photocell: Photocell) -> None:
        super().__init__()

        self.parent = parent
        self.photocell = photocell

        self.image = self.parent.image.copy()
        self.rect = self.image.get_rect()

        scale_img_path = os.path.join(img_dir, "scale_line.png")
        scale_img = pg.image.load(scale_img_path)

        self.light_intensity_slider = Slider(scale_img, 0, 100, "%")
        self.wavelength_slider = Slider(scale_img, 280, 750, "nm")
        self.voltage_slider = Slider(scale_img, 0.1, 10, "mV", accuracy=1)
        self.widgets = [self.light_intensity_slider, self.wavelength_slider, self.voltage_slider]

        self.arrange()

        self.listening_to_event = None

    def arrange(self):
        row_h = int(self.rect.height / len(self.widgets))
        row_y = int(row_h / 2)
        column_x = self.rect.centerx

        for i, w in enumerate(self.widgets):
            if i:
                row_y += row_h

            w.rect.center = column_x, row_y
            self.image.blit(w.image, w.rect)

    def refresh(self):
        [self.image.blit(w.image, w.rect) for w in self.widgets]

    def handle_input(self, pos: Tuple[int], type: str):
        pos_x = pos[0] - self.rect.topleft[0]
        pos_y = pos[1] - self.rect.topleft[1]
        pos = pos_x, pos_y

        if type == "start" and not self.listening_to_event:
            for w in self.widgets:
                if w.rect.collidepoint(pos):
                    w.handle_input(pos, type)
                    if w.ongoing_input:
                        self.listening_to_event = w

        elif self.listening_to_event:
            w_new_value = self.listening_to_event.handle_input(pos, type)

            if w_new_value:
                if self.listening_to_event == self.light_intensity_slider:
                    self.photocell.light_performance = (w_new_value/100) * 5e19
                if self.listening_to_event == self.wavelength_slider:
                    self.photocell.wave_length = w_new_value
                if self.listening_to_event == self.voltage_slider:
                    self.photocell.voltage = w_new_value*1e-3
                
                self.listening_to_event = None

            self.photocell.render_photocell()
            self.refresh()

        self.parent.refresh()


class MaterialButton(pg.sprite.Sprite):
    def __init__(self, name: str) -> None:
        super().__init__()

        self.image = pg.Surface((40, 40))
        self.image.fill((0, 0, 0))
        self.image.set_clip(pg.Rect(2, 2, 36, 36))
        self.rect = self.image.get_rect()

        self.name = name
        self.text = font_button.render(self.name, True, (0, 0, 0))
        self.textpos = self.text.get_rect(center=self.rect.center)

        self.render_inactive()

    def render_inactive(self):
        self.image.fill((255, 255, 255))
        self.image.blit(self.text, self.textpos)

    def render_active(self):
        self.image.fill((200, 200, 255))
        self.image.blit(self.text, self.textpos)


class MaterialSelector(pg.sprite.Sprite):
    name = "catode"
    def __init__(self, parent: pg.sprite.Sprite, photocell: Photocell) -> None:
        super().__init__()

        materials = ['Al', 'Au', 'As', 'Ba', 'Be', 'Cs', 'Ce', 'Eu', 'Ag', 'Ga', 'Ge', 'Hf', 'Ca', 'K', 'Hg', 'Pb']

        self.parent = parent
        self.photocell = photocell

        original_image = self.parent.image.copy()
        original_rect = original_image.get_rect()
        self.image = pg.transform.scale(original_image, (600, 300))
        self.rect = self.image.get_rect(center=original_rect.center)

        self.buttons = pg.sprite.Group()        
        for m in materials:
            self.buttons.add(MaterialButton(m))

        self.active = self.buttons.sprites()[0]
        self.active.render_active()

        self.arrange()

        self.mouse_start = None

    def arrange(self):
        sprites = self.buttons.sprites()
        cell_w = cell_h = 44
        cols = int(self.image.get_width() / cell_w)
        rows = int(len(self.buttons) / cols) + 1
        
        for y in range(rows):
            for x in range(cols):
                rect = pg.Rect(cell_w*x, cell_h*y, cell_w, cell_h)
                try:
                    widget = sprites.pop(0)
                except IndexError:
                    break
                widget.rect.center = rect.center
                self.image.blit(widget.image, widget.rect)

    def change_active(self, to: MaterialButton):
        self.active.render_inactive()
        to.render_active()
        self.active = to

        self.arrange()

        self.photocell.catode_mat = self.active.name
        self.photocell.refresh_catode()

    def handle_input(self, pos: Tuple[int], type: str):
        pos_x = pos[0] - self.rect.topleft[0]
        pos_y = pos[1] - self.rect.topleft[1]
        pos = pos_x, pos_y

        if type == "start":
            self.mouse_start = pos

        if type == "stop":
            for b in self.buttons:
                if b.rect.collidepoint(self.mouse_start):
                    self.change_active(b)

            self.parent.refresh()


class Canvas(pg.sprite.Sprite):
    def __init__(self, image: pg.Surface, photocell: Photocell, topleft: Tuple[int] = (0, 0), active: str = 'light') -> None:
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(topleft=topleft)

        self.states = {
            "light": LightSettings(self, photocell),
            "catode": MaterialSelector(self, photocell)
        }
        self.active = self.states[active]
        self.refresh()

    def change_active(self, to: str):
        self.active = self.states[to]
        self.refresh()

    def refresh(self):
        self.image.fill((255, 255, 255))
        self.image.blit(self.active.image, self.active.rect)

    def handle_input(self, pos: Tuple[int], type: str):
        pos_x = pos[0] - self.rect.topleft[0]
        pos_y = pos[1] - self.rect.topleft[1]
        pos = pos_x, pos_y

        self.active.handle_input(pos, type)


class Settings(pg.sprite.Sprite):
    def __init__(self, photocell) -> None:
        super().__init__()

        self.image = pg.Surface((1000, 350))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=(0, 450))

        menu_img = pg.Surface((300, 350))
        menu_img.fill((255, 255, 255))
        light_button = MenuButton(self, "light", "Light and Voltage")
        catode_button = MenuButton(self, "catode", "Catode Material")
        self.menu = Menu(menu_img, (0, 0), light_button, catode_button)

        canvas_img = pg.Surface((700, 350))
        canvas_img.fill((255, 255, 255))
        canvas_pos = (300, 0)
        self.canvas = Canvas(canvas_img, photocell, canvas_pos, self.menu.active.name)

        self.refresh_settings()

        self.mouse_start = None

    def refresh_settings(self):
        self.image.blit(self.menu.image, self.menu.rect)
        self.image.blit(self.canvas.image, self.canvas.rect)

    def handle_input(self, pos: Tuple[int], type: str):
        pos_x = pos[0] - self.rect.topleft[0]
        pos_y = pos[1] - self.rect.topleft[1]
        pos = pos_x, pos_y

        if type == "mousestart":
            self.mouse_start = pos

            if self.canvas.rect.collidepoint(*pos):
                self.canvas.handle_input(self.mouse_start, 'start')

        if type == "mousestop":
            if self.menu.rect.collidepoint(*self.mouse_start):
                self.menu.clicked(self.mouse_start)
                self.canvas.change_active(self.menu.active.name)

            if self.canvas.rect.collidepoint(*self.mouse_start):
                self.canvas.handle_input(pos, 'stop')

        if self.canvas.rect.collidepoint(*self.mouse_start) and type == "mousepos":
            self.canvas.handle_input(pos, 'pos')

        self.refresh_settings()