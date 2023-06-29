cd sadtalker
call conda activate sadtalker
python inference.py --driven_audio d:\ai\discordbot\noplayerfound\dmasterresponse.mp3 --size 256 --source_image alice.png --preprocess resize
call conda deactivate
EXIT /B 0