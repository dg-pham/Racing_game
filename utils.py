import pygame


def scale_image(img, factor):
    # round img size
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(win, image, top_Left, angle):
    # rotate
    rotated_image = pygame.transform.rotate(image, angle)
    # Returns a new rectangle covering the entire rotated_image when its center = origin image's center
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_Left).center)
    win.blit(rotated_image, new_rect.topleft)


def blit_text_center(win, font, text):
    # render text to screen
    render = font.render(text, 1, (200, 200, 200))
    win.blit(render, (win.get_width() / 2 - render.get_width() /
                      2, win.get_height() / 2 - render.get_height() / 2))
