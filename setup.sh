sudo apt update
sudo apt install python3-pip

sudo apt install -y --no-install-recommends python3-pil gstreamer1.0-gl gstreamer1.0-opencv gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools libgstreamer-plugins-base1.0-dev libgstreamer1.0-0 libgstreamer1.0-dev


sudo pip3 install --extra-index-url https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2024/simple/ robotpy

sudo cp scripts/snowshot_runner.service /lib/systemd/system/snowshot_runner.service
sudo chmod 644 /lib/systemd/system/snowshot_runner.service
sudo systemctl daemon-reload
sudo systemctl enable snowshot_runner.service