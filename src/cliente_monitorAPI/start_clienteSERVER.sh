#/bin/bash
for var in $(ccrypt -d -c ../settings.env.cpt); do
        export "$var"
done

python3.7 manage.py runserver 0.0.0.0:9000
