echo " BUILD START"
python3.9 -m pip install -U pip
# pip3 install pysqlite3
python3.9 -m pip install -r requirements.txt
# python3.9 manage.py collectstatic --noinput --clear
echo " BUILD"
python3.9 manage.py makemigrations
python3.9 manage.py migrate

echo " BUILDcollectstatic "
python3.9 manage.py collectstatic