# copied from http://stackoverflow.com/questions/2648151/python-frequency-detection

from datetime import datetime, timedelta
from Queue import Queue
import audioop
import time
import wave

import numpy as np
import pyaudio

import lights

WIDTH = 2
RATE = 44100
CHUNK = 1024
window = np.blackman(CHUNK)

MIN_FREQUENCY = 60
MAX_FREQUENCY = 1800
MIN_VOLUME = 100
MAX_VOLUME = 500

last_change_time = datetime.now()
frequencies_queue = Queue()
volumes_queue = Queue()

def main():
    p = pyaudio.PyAudio()

    device_info = p.get_device_info_by_index(2)
    channels = int(device_info['maxInputChannels'])

    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=channels,
                    rate=RATE,
                    input_device_index=2,
                    input=True,
                    stream_callback=callback)

    stream.start_stream()

    while stream.is_active():
        pass

    stream.stop_stream()
    stream.close()

    p.terminate()

def callback(in_data, frame_count, time_info, status):
    global last_change_time
    global frequencies_queue
    global volumes_queue

    # unpack the data and times by the hamming window
    indata = np.array(wave.struct.unpack("%dh"%(len(in_data)/WIDTH), in_data))*window

    # Take the fft and square each value
    fftData = abs(np.fft.rfft(indata))**2

    # find the maximum
    which = fftData[1:].argmax() + 1

    # use quadratic interpolation around the max
    if which != len(fftData)-1:
        y0,y1,y2 = np.log(fftData[which-1:which+2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        frequency = (which+x1)*RATE/CHUNK
    else:
        frequency = which*RATE/CHUNK

    if frequency > MIN_FREQUENCY and frequency < MAX_FREQUENCY:
        # get volume
        volume = audioop.rms(in_data, WIDTH)
        volumes_queue.put(volume)

        frequencies_queue.put(frequency)

        bri = 235
        sat = 254
        time_now = datetime.now()
        if time_now >= last_change_time + timedelta(seconds=0.3):
            frequencies = []
            while not frequencies_queue.empty():
                frequencies.append(frequencies_queue.get())

            freq_min = min(frequencies)
            freq_max = max(frequencies)
            try:
                frequencies.remove(freq_min)
                frequencies.remove(freq_max)
            except ValueError:
                pass

            volumes = []
            while not volumes_queue.empty():
                volumes.append(volumes_queue.get())

            vol_min = min(volumes)
            vol_max = max(volumes)
            try:
                volumes.remove(vol_min)
                volumes.remove(vol_max)
            except ValueError:
                pass

            if frequencies and volumes:
                freq_avg = sum(frequencies) / float(len(frequencies))
                vol_avg = sum(volumes) / float(len(volumes))

                hue = int((freq_avg - MIN_FREQUENCY) / float(MAX_FREQUENCY) * 65535)
                bri = int((vol_avg - MIN_VOLUME) / float(MAX_VOLUME) * 255)
                if bri < 0: bri = 0
                if bri > 254: bri = 254
                print 'Frequency:', freq_avg, 'Hue:', hue, 'Bri:', bri

                lights.change_hue_single(hue=hue, bri=bri)
            last_change_time = time_now

    return (in_data, pyaudio.paContinue)

if __name__ == '__main__':
    main()
