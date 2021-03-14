import subprocess
import sys
from tkinter import messagebox

# install the necessary packages if they are not installed
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('numpy')
install('pillow')
install('shapely')
messagebox.showinfo('Note',"All needed packages have been installed,\nYou can run the project now")