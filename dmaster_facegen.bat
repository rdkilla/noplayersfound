cd sadtalker
call conda activate sadtalker
python inference.py --driven_audio d:\ai\discordbot\noplayerfound\dmasterresponse.wav --size 256 --result_dir ./dmasterresults --source_image alice.png --facerender pirender
call conda deactivate
EXIT /B 0