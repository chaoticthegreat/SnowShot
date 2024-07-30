sudo apt update
sudo apt install python3-pip

sudo apt install -y --no-install-recommends python3-pil gstreamer1.0-gl gstreamer1.0-opencv gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools libgstreamer-plugins-base1.0-dev libgstreamer1.0-0 libgstreamer1.0-dev


sudo pip3 install --extra-index-url https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2024/simple/ robotpy


pip install ultralytics[export]
pip uninstall torch torchvision

sudo apt-get install -y libopenblas-base libopenmpi-dev
wget https://developer.download.nvidia.com/compute/redist/jp/v512/pytorch/torch-2.1.0a0+41361538.nv23.06-cp38-cp38-linux_aarch64.whl -O torch-2.1.0a0+41361538.nv23.06-cp38-cp38-linux_aarch64.whl
pip install torch-2.1.0a0+41361538.nv23.06-cp38-cp38-linux_aarch64.whl

sudo apt install -y libjpeg-dev zlib1g-dev
git clone https://github.com/pytorch/vision torchvision
cd torchvision
git checkout v0.16.2
python3 setup.py install --user
cd ..

wget https://nvidia.box.com/shared/static/zostg6agm00fb6t5uisw51qi6kpcuwzd.whl -O onnxruntime_gpu-1.17.0-cp38-cp38-linux_aarch64.whl
pip install onnxruntime_gpu-1.17.0-cp38-cp38-linux_aarch64.whl
pip install numpy==1.23.5



sudo cp scripts/snowshot_runner.service /lib/systemd/system/snowshot_runner.service
sudo chmod 644 /lib/systemd/system/snowshot_runner.service
sudo systemctl daemon-reload
sudo systemctl enable snowshot_runner.service