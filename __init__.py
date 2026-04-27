"""
    EZSmolagents makes smolagents easy.
    Copyright (C) 2026  JohnnyTech Systems OSS
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
from .runners.Runner import Runner
from .runners.DockerRunner import DockerRunnerFrontend
from .runners.LocalRunner import LocalRunnerFrontend
import os
from rich import inspect, print
import webbrowser as webbrowser
import inspect
import importlib
from easyrun import run_simple, run_simple_stream, run_local, run_local_stream
#Utils
def get_paths_for_required_package_files():
    """Returns a list of paths for files that are required for the package to function. This is used for copying the package into the Docker container."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)))
def get_importer_filename():
    for frame_info in inspect.stack():
        fname = frame_info.filename
        if "_bootstrap" not in fname and fname != __file__:
            return fname
    return None
def easteregg():
    print(r"""[bold magenta]          _____                    _____                    _____                    _____                   _______                   _____            _____                    _____                    _____                    _____                _____                    _____          
         /\    \                  /\    \                  /\    \                  /\    \                 /::\    \                 /\    \          /\    \                  /\    \                  /\    \                  /\    \              /\    \                  /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\               /::::\    \               /::\____\        /::\    \                /::\    \                /::\    \                /::\____\            /::\    \                /::\    \        
       /::::\    \               \:::\    \              /::::\    \              /::::|   |              /::::::\    \             /:::/    /       /::::\    \              /::::\    \              /::::\    \              /::::|   |            \:::\    \              /::::\    \       
      /::::::\    \               \:::\    \            /::::::\    \            /:::::|   |             /::::::::\    \           /:::/    /       /::::::\    \            /::::::\    \            /::::::\    \            /:::::|   |             \:::\    \            /::::::\    \      
     /:::/\:::\    \               \:::\    \          /:::/\:::\    \          /::::::|   |            /:::/~~\:::\    \         /:::/    /       /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \          /::::::|   |              \:::\    \          /:::/\:::\    \     
    /:::/__\:::\    \               \:::\    \        /:::/__\:::\    \        /:::/|::|   |           /:::/    \:::\    \       /:::/    /       /:::/__\:::\    \        /:::/  \:::\    \        /:::/__\:::\    \        /:::/|::|   |               \:::\    \        /:::/__\:::\    \    
   /::::\   \:::\    \               \:::\    \       \:::\   \:::\    \      /:::/ |::|   |          /:::/    / \:::\    \     /:::/    /       /::::\   \:::\    \      /:::/    \:::\    \      /::::\   \:::\    \      /:::/ |::|   |               /::::\    \       \:::\   \:::\    \   
  /::::::\   \:::\    \               \:::\    \    ___\:::\   \:::\    \    /:::/  |::|___|______   /:::/____/   \:::\____\   /:::/    /       /::::::\   \:::\    \    /:::/    / \:::\    \    /::::::\   \:::\    \    /:::/  |::|   | _____        /::::::\    \    ___\:::\   \:::\    \  
 /:::/\:::\   \:::\    \               \:::\    \  /\   \:::\   \:::\    \  /:::/   |::::::::\    \ |:::|    |     |:::|    | /:::/    /       /:::/\:::\   \:::\    \  /:::/    /   \:::\ ___\  /:::/\:::\   \:::\    \  /:::/   |::|   |/\    \      /:::/\:::\    \  /\   \:::\   \:::\    \ 
/:::/__\:::\   \:::\____\_______________\:::\____\/::\   \:::\   \:::\____\/:::/    |:::::::::\____\|:::|____|     |:::|    |/:::/____/       /:::/  \:::\   \:::\____\/:::/____/  ___\:::|    |/:::/__\:::\   \:::\____\/:: /    |::|   /::\____\    /:::/  \:::\____\/::\   \:::\   \:::\____\
\:::\   \:::\   \::/    /\::::::::::::::::::/    /\:::\   \:::\   \::/    /\::/    / ~~~~~/:::/    / \:::\    \   /:::/    / \:::\    \       \::/    \:::\  /:::/    /\:::\    \ /\  /:::|____|\:::\   \:::\   \::/    /\::/    /|::|  /:::/    /   /:::/    \::/    /\:::\   \:::\   \::/    /
 \:::\   \:::\   \/____/  \::::::::::::::::/____/  \:::\   \:::\   \/____/  \/____/      /:::/    /   \:::\    \ /:::/    /   \:::\    \       \/____/ \:::\/:::/    /  \:::\    /::\ \::/    /  \:::\   \:::\   \/____/  \/____/ |::| /:::/    /   /:::/    / \/____/  \:::\   \:::\   \/____/ 
  \:::\   \:::\    \       \:::\~~~~\~~~~~~         \:::\   \:::\    \                  /:::/    /     \:::\    /:::/    /     \:::\    \               \::::::/    /    \:::\   \:::\ \/____/    \:::\   \:::\    \              |::|/:::/    /   /:::/    /            \:::\   \:::\    \     
   \:::\   \:::\____\       \:::\    \               \:::\   \:::\____\                /:::/    /       \:::\__/:::/    /       \:::\    \               \::::/    /      \:::\   \:::\____\       \:::\   \:::\____\             |::::::/    /   /:::/    /              \:::\   \:::\____\    
    \:::\   \::/    /        \:::\    \               \:::\  /:::/    /               /:::/    /         \::::::::/    /         \:::\    \              /:::/    /        \:::\  /:::/    /        \:::\   \::/    /             |:::::/    /    \::/    /                \:::\  /:::/    /    
     \:::\   \/____/          \:::\    \               \:::\/:::/    /               /:::/    /           \::::::/    /           \:::\    \            /:::/    /          \:::\/:::/    /          \:::\   \/____/              |::::/    /      \/____/                  \:::\/:::/    /     
      \:::\    \               \:::\    \               \::::::/    /               /:::/    /             \::::/    /             \:::\    \          /:::/    /            \::::::/    /            \:::\    \                  /:::/    /                                 \::::::/    /      
       \:::\____\               \:::\____\               \::::/    /               /:::/    /               \::/____/               \:::\____\        /:::/    /              \::::/    /              \:::\____\                /:::/    /                                   \::::/    /       
        \::/    /                \::/    /                \::/    /                \::/    /                 ~~                      \::/    /        \::/    /                \::/____/                \::/    /                \::/    /                                     \::/    /        
         \/____/                  \/____/                  \/____/                  \/____/                                           \/____/          \/____/                                           \/____/                  \/____/                                       \/____/         
                                                                                                                                                                                                                                                                                      [/bold magenta]""")
  
    webbrowser.open("https://patorjk.com/misc/scrollingtext/timewaster.php?text=JohnnyTech+Systems&autoscroll=ON&duration=20")
importer_filename = get_importer_filename()
#Regular __init__.py stuff is here now
DebugRunner = Runner #Runner is just my internal naming for the base Runner class, which should not be used directly and is debug only.
DockerRunner = DockerRunnerFrontend #DockerRunnerFrontend is just my internal naming because I do not want to confuse DockerRunner with the backend Runner class.
LocalRunner = LocalRunnerFrontend #LocalRunnerFrontend is the user-facing local runner
__all__ = ["DockerRunner", "LocalRunner", "easteregg", "DebugRunner"]
