for var in $(ccrypt -d -c settings_terminal.env.cpt); do
    export "$var"
done

docker-compose up
