cd sadtalker
call conda activate sadtalker
python inference.py --driven_audio d:\ai\discordbot\noplayerfound\playerinput.mp3 --size 256 --result_dir ./playerresults --source_image player.png --preprocess resize
call conda deactivate
EXIT /B 0