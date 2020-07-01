rem start anaconda bat file.change directories by computers
call C:\Users\owner\Miniconda3\Scripts\activate.bat
call conda activate ml_py37
:search
python app.py
timeout 120

goto search