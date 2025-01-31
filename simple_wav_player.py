import threading
import time
import wave
from time import sleep

import pyaudio

import threading
import time



class WavPlayer:
    def __init__(self, file_path, get_playing):
        """
        Initialize the WavPlayer for simple playback.
        :param file_path: Path to the .wav file to be loaded
        """
        self.file_path = file_path
        self._wave_file = wave.open(self.file_path, 'rb')  # Load the .wav file
        self.pa = pyaudio.PyAudio()  # Initialize PyAudio
        self.stream = None
        self.__get_playing = get_playing

    def play(self):
        """
        Play the audio file from start to finish.
        """
        # Open an audio stream
        self.stream = self.pa.open(
            format=self.pa.get_format_from_width(self._wave_file.getsampwidth()),
            channels=self._wave_file.getnchannels(),
            rate=self._wave_file.getframerate(),
            output=True
        )

        chunk_size = 1024  # Read audio in chunks
        data = self._wave_file.readframes(chunk_size)

        # Play the audio file
        # t = time.time()
        while data:
            # print("working")
            # if 6.0 > time.time() - t > 5.0:
            #     self.dynamic_update()
            #     # self.stop()
            #     while True:
            #         if time.time() - t >= 6.0:
            #             break
            #         pass
            if not self.__get_playing():
                while True:
                    sleep(0.5)
                    if self.__get_playing():
                        break

            self.stream.write(data)
            data = self._wave_file.readframes(chunk_size)

        # Clean up the stream once playback finishes
        self.stop()

    def dynamic_update(self):
        # print("dy")
        pass


    def stop(self):
        """
        Stop playback and clean up resources.
        """
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self._wave_file:
            self._wave_file.close()
            self._wave_file = None



    def __del__(self):
        """
        Ensure resources are closed when the object is deleted.
        """
        self.stop()
        if self.pa:
            self.pa.terminate()



class PlayerPlayer(threading.Thread):

    def is_playing(self):
        return self.playing

    def __init__(self):
        super().__init__()
        self._playing = False  # 使用私有属性以限制直接访问
        self._lock = threading.Lock()  # 初始化锁
        self.player = WavPlayer("Hacking.wav", self.is_playing)


    @property
    def playing(self):
        """线程安全获取 playing 状态"""
        with self._lock:  # 自动加锁和解锁
            return self._playing

    @playing.setter
    def playing(self, value):
        """线程安全设置 playing 状态"""
        with self._lock:  # 自动加锁和解锁
            self._playing = value

    def run(self):
        self.player.play()
        pass


# Usage Example
if __name__ == "__main__":
    p = PlayerPlayer()
    p.start()

    while True:
        p.playing = False
        sleep(1)
        p.playing = True
        sleep(1)

    p.join()

