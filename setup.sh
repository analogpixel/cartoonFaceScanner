python3 -m venv dlib
cd dlib
brew install python3 --framework
brew install cmake
brew install boost
brew install boost-python --with-python3
source bin/activate
pip install dlib
pip install imutils
pip install numpy
pip install opencv-python
pip install -U wxPython

# https://www.raspberrypi.org/forums/viewtopic.php?t=120208
# window manager setup
apt-get install i3
update-alternatives --config x-window-manager

echo "
[Desktop]
Session=i3
" > /home/pi/.dmrc


