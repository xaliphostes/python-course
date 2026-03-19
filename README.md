# Python course

## Installation

1. Install Visual Studio Code (VS Code)
2. Install Python version >= 3.11
3. Launch VS Code
4. Show the terminal of VS Code (Ctrl-j)
5. Go to the folder of your choice for developping
6. Create the virtual env for Python (only once)
   ```sh
   python -m venv venv312
   ```
7. Activate the venv (Linux/macos) for any opened terminal
   ```sh
   source venv312/bin/activate
   ```
8. Activate for Windobe$
   
   Run only once
   ```sh
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

   Then, activate for any terminal
   ```sh
   .\venv312\Sctipts\activate
   ```

## Libraries needed

1. numpy
   
2. matplotlib
3. pandas

## Files

1. `test.py`: plotting a curve
   
2. `shear.py`: plotting shear and normal stress
3. `myStressLib.py`: provide some basic functions and one class to play with (used in `inversion.py` and `plotDomain.py`)
4. `inversion.py`: perform regional paleo stress inversion
5. `plotDomain.py`: plot a specific domain for stress inversion
6. `gui_inversion.py`: a GUI to perform the stress inversion with plotting
7. `veins.csv`: some veins at Les Matelles
8. `stylolites.csv`: some stylolites at Les Matelles