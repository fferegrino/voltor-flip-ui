from fbs_runtime.application_context.PyQt5 import ApplicationContext

import sys

from voltorb_flip_ui.game_widget import GameWidget

if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext

    game = GameWidget(appctxt)

    sys.exit(game.run())