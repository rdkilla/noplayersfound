cd sadtalker
call conda activate sadtalker
python inference.py --driven_audio d:\ai\discordbot\noplayerfound\playerinput.wav --size 256 --facerender pirender --result_dir ./playerresults --source_image player.png
call conda deactivate
EXIT /B 0