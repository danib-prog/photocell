import pygame as pg
import sprites
import os
import sys


if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


def main():
    fps = 60
    timescale = 2e-5
    pg.init()
    clock = pg.time.Clock()

    screen = pg.display.set_mode((1000, 800), pg.SCALED)
    screen.fill((255, 255, 255))

    photocell = sprites.Photocell()
    screen.blit(photocell.image, photocell.rect)

    settings = sprites.Settings(photocell)
    screen.blit(settings.image, settings.rect)

    electron_group = pg.sprite.Group()

    run = True
    tracking_mouse = False

    while run:    
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                settings.handle_input(event.pos, 'mousestart')
                tracking_mouse = True

            if event.type == pg.MOUSEBUTTONUP:
                settings.handle_input(event.pos, 'mousestop')
                tracking_mouse = False

        if tracking_mouse:
            settings.handle_input(pg.mouse.get_pos(), 'mousepos')

        electrons = photocell.update((1/fps)*timescale)
        electron_group.update((1/fps)*timescale, photocell.voltage)
        electron_group.add(*electrons)
        
        photocell.render_current()
        photocell.render_voltage()
        screen.blit(photocell.image, photocell.rect)
        electron_group.draw(screen)

        screen.blit(settings.image, settings.rect)        
        
        pg.display.flip()

    clock.tick(fps)


if __name__ == '__main__':
    main()