import game
import score
import pygame


pygame.init()

FramePerSec = pygame.time.Clock()


def update_game_display():
    pygame.display.update()
    FramePerSec.tick(game.FPS)


def main():
    while True:
        if game.GlobalState.GAME_STATE == game.GameStatus.MAIN_MENU:
            game.main_menu_phase()
        elif game.GlobalState.GAME_STATE == game.GameStatus.GAMEPLAY:
            game.gameplay_phase()
        elif game.GlobalState.GAME_STATE == game.GameStatus.GAME_END:
            game.exit_game_phase()

        update_game_display()


if __name__ == "__main__":
    main()
