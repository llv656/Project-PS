#/bin/bash
for var in $(ccrypt -d -c ../settings.env.cpt); do
        export "$var"
done

python3.7 manage.py migrate
python3.7 manage.py makemigrations

