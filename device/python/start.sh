source /opt/SmartHouseSystem/device/python/venv/bin/activate

export PYTHONPATH="/opt/SmartHouseSystem"

python3 /opt/SmartHouseSystem/device/python/main.py arg1 arg2
if [ $? -ne 0 ]; then
    echo "Python script failed!"
    exit 1
fi