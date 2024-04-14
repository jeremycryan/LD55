import pygame

import constants as c
import frame as f
import sys
from sound_manager import SoundManager
from image_manager import ImageManager
import asyncio

from twitch_stream_chat import Stream


class Game:
    def __init__(self):
        pygame.init()
        SoundManager.init()
        ImageManager.init()
        self.pre_screen = pygame.Surface(c.WINDOW_SIZE)
        self.screen = pygame.display.set_mode(c.DISPLAY_SIZE)
        pygame.display.set_caption(c.CAPTION)
        self.clock = pygame.time.Clock()
        self.teams = {0:[], 1:[]}
        pygame.mixer.init()
        pygame.mixer.music.load("audio/music.ogg")
        pygame.mixer.music.play(-1)

        self.stream = None
        self.restart_stream()

        self.main()

    def restart_stream(self):
        if self.stream:
            self.stream.close()
        self.stream = Stream()
        self.stream.open("plasmastarfish")

    def main(self):
        current_frame = f.ShopFrame(self)
        current_frame.load()
        self.clock.tick(60)

        while True:
            dt, events = self.get_events()
            if dt == 0:
                dt = 1/100000
            pygame.display.set_caption(f"{c.CAPTION} ({int(1/dt)} FPS)")
            if dt > 0.05:
                dt = 0.05
            current_frame.update(dt, events)
            if c.DEBUG:
                current_frame.draw(self.pre_screen, (0, 0))
                self.screen.blit(pygame.transform.scale(self.pre_screen, (c.DISPLAY_SIZE)), (0, 0))
            else:
                current_frame.draw(self.screen, (0, 0))
            pygame.display.flip()

            if current_frame.done:
                current_frame = current_frame.next_frame()
                current_frame.load()

    def get_events(self):
        dt = self.clock.tick(c.FRAMERATE)/1000

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4:
                    pygame.display.toggle_fullscreen()

        messages = self.stream.queue_flush()
        for message in messages:
            events.append(CustomEvent(message))
            print(message)

        return dt, events


class CustomEvent:
    def __init__(self, message):
        self.type = "Twitch"
        self.message = message


if __name__=="__main__":
    Game()