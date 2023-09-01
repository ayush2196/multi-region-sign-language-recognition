# SpeakSign

This project is a part of my Thesis, where several research work and implementations are done on Sign language Recognition and Translation (Citations are given) and demo application is made on text to Sign language conversion.

# Installation
This project needs flask and python to run.

```sh
pip install -r requirements.txt
pip install spacy
python main.py
```
After running ```main.py``` stanford parser will be downloaded 
you may run into some errors related to classpath of java, google them they shouldn't be so hard to fix 
Open the browser and go to http://127.0.0.1:5000/  and see the project in action.

## NOTE
The project uses SIGML files for animating the words and they may not be accurate as making SIGML through HamNoSys is a long and tedious task and whoever made the sigml files which this project uses may not be accurate. 

## Credits
SIGML player: - https://vh.cmp.uea.ac.uk/index.php/CWA_Signing_Avatars
