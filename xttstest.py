from TTS.api import TTS
tts = TTS("xtts_v2", gpu=True)

# generate speech by cloning a voice using default settings
tts.tts_to_file(text="hey there dixie normus and katjatjay, i wanted to wish you many victory royales in your quest for more cheeks to clap!",
                file_path="output1112.wav",
                speaker_wav="clapping.wav",
                language="en")