import random
import pyasge
import asyncio
from gamedata import GameData


def isInside(sprite, mouse_x, mouse_y) -> bool:
    # grab the bounding box of the current sprite
    bounds = sprite.getWorldBounds()

    if bounds.v1.x < mouse_x < bounds.v2.x and bounds.v1.y < mouse_y < bounds.v3.y:
        return True

    return False

    pass


class MyASGEGame(pyasge.ASGEGame):
    """
    The main game class
    """

    def __init__(self, settings: pyasge.GameSettings):
        """
        Initialises the game and sets up the shared data.

        Args:
            settings (pyasge.GameSettings): The game settings
        """
        pyasge.ASGEGame.__init__(self, settings)
        self.renderer.setClearColour(pyasge.COLOURS.YELLOW)

        # create a game data object, we can store all shared game content here
        self.data = GameData()
        self.data.inputs = self.inputs
        self.data.renderer = self.renderer
        self.data.game_res = [settings.window_width, settings.window_height]

        # register the key and mouse click handlers for this class
        self.key_id = self.data.inputs.addCallback(pyasge.EventType.E_KEY, self.keyHandler)
        self.mouse_id = self.data.inputs.addCallback(pyasge.EventType.E_MOUSE_CLICK, self.clickHandler)

        # set the game to the menu
        self.menu = True
        self.play_option = None
        self.exit_option = None
        self.menu_option = 0

        # Spawn in the visuals for the background
        self.data.background = pyasge.Sprite()
        self.initBackground()

        # Create a menu object
        self.menu_text = None
        self.initMenu()

        # Create a scoreboard object
        self.scoreboard = None
        self.initScoreboard()

        # Create a timer object
        self.timer = None
        self.initTimer()

        # Configurable amount of fish can be spawned in
        self.fish = []
        self.fish_num = 5
        for i in range(self.fish_num):
            self.fish.append(pyasge.Sprite())

            self.initFish(i)

    def initBackground(self) -> bool:
        if self.data.background.loadTexture("/data/images/background.png"):
            # prioritise rendering this background first, once it has loaded successfully
            self.data.background.z_order = -100
            return True
        else:
            return False

    def initFish(self, fish_id) -> bool:

        if self.fish[fish_id].loadTexture("/data/images/kenney_fishpack/fishTile_073.png"):
            self.fish[fish_id].z_order = 1
            self.fish[fish_id].scale = 1
            self.fish[fish_id].x = 300
            self.fish[fish_id].y = 300
            self.spawn(fish_id)
            return True

        return False

    def initMenu(self) -> bool:
        self.data.fonts["MainFont"] = self.renderer.loadFont("/data/fonts/KGHAPPY.ttf", 64)
        self.menu_text = pyasge.Text(self.data.fonts["MainFont"])
        self.menu_text.string = "The Fish Game"
        self.menu_text.position = [100, 100]
        self.menu_text.colour = pyasge.COLOURS.HOTPINK

        # Button for starting the game
        self.play_option = pyasge.Text(self.data.fonts["MainFont"])
        self.play_option.string = "START"
        self.play_option.position = [100, 400]
        self.play_option.colour = pyasge.COLOURS.HOTPINK

        # Button for exiting the game
        self.exit_option = pyasge.Text(self.data.fonts["MainFont"])
        self.exit_option.string = "EXIT"
        self.exit_option.position = [500, 400]
        self.exit_option.colour = pyasge.COLOURS.HOTPINK

        return True

    def initScoreboard(self) -> None:
        self.scoreboard = pyasge.Text(self.data.fonts["MainFont"])
        self.scoreboard.x = 1300
        self.scoreboard.y = 75
        self.scoreboard.string = str(self.data.score).zfill(6)

        pass

    def initTimer(self) -> None:
        self.timer = pyasge.Text(self.data.fonts["MainFont"])
        self.timer.x = 1300
        self.timer.y = 100
        self.timer.string = str(self.data.timer)

    def clickHandler(self, event: pyasge.ClickEvent) -> None:
        # check to see if mouse button 1 is being pressed
        if event.action == pyasge.MOUSE.BUTTON_PRESSED and \
           event.button == pyasge.MOUSE.MOUSE_BTN1:

            # check the mouse position is inside of one of the sprite's bounding box
            if len(self.fish) > 0:
                for i in range(self.fish_num):
                    if isInside(self.fish[i], event.x, event.y):
                        self.data.score += 1
                        self.scoreboard.string = str(self.data.score).zfill(6)
                        self.spawn(i)  # put the fish in a different position to continue the game
        pass

    def keyHandler(self, event: pyasge.KeyEvent) -> None:

        # only act when the key is pressed, as opposed to being released
        if event.action == pyasge.KEYS.KEY_PRESSED:

            # check for both the left and right arrow keys, to cycle between the play/exit buttons
            if event.key == pyasge.KEYS.KEY_RIGHT or event.key == pyasge.KEYS.KEY_LEFT:
                self.menu_option = 1 - self.menu_option
                if self.menu_option == 0:
                    self.play_option.string = "START"
                    self.play_option.colour = pyasge.COLOURS.HOTPINK
                    self.exit_option.string = ">EXIT"
                    self.exit_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY
                else:
                    self.play_option.string = ">START"
                    self.play_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY
                    self.exit_option.string = "EXIT"
                    self.exit_option.colour = pyasge.COLOURS.HOTPINK

            # if the enter key is then pressed, load the corresponding menu option action
            if event.key == pyasge.KEYS.KEY_ENTER:
                if self.menu_option == 1:
                    self.menu = False
                else:
                    self.signalExit()

            # debug testing for random spawn positions
            if event.key == pyasge.KEYS.KEY_R:
                self.spawn()

        pass

    def spawn(self, fish_id) -> None:
        # generate random coordinates (x,y) for the fish to spawn in (ensuring the fish does not spawn on edges)
        # reduced margin of spawning error with multiplication
        x = random.randint(0, self.data.game_res[0] - self.fish[fish_id].width * 2)
        y = random.randint(0, self.data.game_res[1] - self.fish[fish_id].height * 2)

        self.fish[fish_id].x = x
        self.fish[fish_id].y = y
        # move_task = asyncio.create_task(self.moveFish(self.fish.x, self.fish.y, x, y))
        pass

    async def moveFish (self, old_x, old_y, new_x, new_y):
        # gradually moves the fish from one position to another
        await asyncio.sleep(2)
        self.fish.x = new_x
        self.fish.y = new_y
        pass

    def update(self, game_time: pyasge.GameTime) -> None:

        if self.menu:
            # update the menu here
            pass
        else:
            # update the game here
            pass

        # timer keeps track of playtime
        self.data.timer += pyasge.GameTime.fixed_delta

    def render(self, game_time: pyasge.GameTime) -> None:
        """
        This is the variable time-step function. Use to update
        animations and to render the gam    e-world. The use of
        ``frame_time`` is essential to ensure consistent performance.
        @param game_time: The tick and frame deltas.
        """

        if self.menu:
            # render the menu here
            self.data.renderer.render(self.data.background)
            self.data.renderer.render(self.menu_text)

            self.data.renderer.render(self.play_option)
            self.data.renderer.render(self.exit_option)
        else:
            # render the game here
            self.data.renderer.render(self.data.background)
            for i in range(self.fish_num):
                self.data.renderer.render(self.fish[i])
            self.data.renderer.render(self.scoreboard)
            pass


def main():
    """
    Creates the game and runs it
    For ASGE Games to run they need settings. These settings
    allow changes to the way the game is presented, its
    simulation speed and also its dimensions. For this project
    the FPS and fixed updates are capped at 60hz and Vsync is
    set to adaptive.
    """
    settings = pyasge.GameSettings()
    settings.window_width = 1600
    settings.window_height = 900
    settings.fixed_ts = 60
    settings.fps_limit = 60
    settings.window_mode = pyasge.WindowMode.BORDERLESS_WINDOW
    settings.vsync = pyasge.Vsync.ADAPTIVE
    game = MyASGEGame(settings)
    game.run()


if __name__ == "__main__":
    main()
