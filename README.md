My apologies for the messy code, I still havent had a chance to clean it/optimize it fully

This is based off the https://github.com/hzeller/rpi-rgb-led-matrix project so the first thing to do is set that up, after that you need to get audio input from your stereo to your Pi, I used a full usb Dock that I had laying around, but something like this should work: https://www.microcenter.com/product/513765/GDL-0424_USB_Stereo_Sound_Card_Adaptor_for_Microphones_and_Headphones?storeID=131&gStoreCode=131&gQT=1

I set that as the default audio input for my Pi, after that all you need to do is install the required Python libraries (it might be a good idea to do this in a Venv as the sounddevice one can be finicky), and cd into the VinylViz folder and run:

sudo python3 audio_processor.py
