from TTS.api import TTS
tts = TTS("xtts_v2", gpu=True)

# generate speech by cloning a voice using default settings
tts.tts_to_file(text="Those sound like great ideas! Incorporating real-world celebrities and historical figures could help ground the game in reality while also making it more memorable and distinctive. Another way to keep the gameplay fresh and varied could be through the introduction of branching storylines or dialogue choices that impact the direction of the narrative. For example, if one party member dies early on, subsequent scenarios could revolve around dealing with the fallout of that loss rather than simply moving forward without consequence. Ultimately, the key to creating a successful game lies in striking a balance between familiar elements and innovation, and incorporating diverse perspectives and approaches to problem solving.which it processes",
                file_path="output1112.wav",
                speaker_wav="quorra.wav",
                language="en")