#!/bin/bash

set -e

# check user
if [ "$(id -u)" -ne 0 ]; then
    echo "[❌] Please run as root!"
    exit 1
fi;
echo "[✅] Running as root!"

# check if user exists
if id "gh_deploy" &>/dev/null; then
    echo "[❌] User gh_deploy already exists! Exiting to prevent overwriting."
    exit 1
fi;
echo "[✅] User gh_deploy does not exist. Continuing..."

# check if .env exists
if [ -f "/opt/anon-confess/.env" ]; then
    echo "[❌] /opt/anon-confess/.env already exists! Exiting to prevent overwriting."
    exit 1
fi;
echo "[✅] /opt/anon-confess/.env does not exist. Continuing..."


# install dependencies
apt-get update
apt-get install -y curl git acl libpq-dev


# install docker
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    echo "[✅] Docker installed!"
else
    echo "[✅] Docker already installed."
fi


# create user
sudo adduser --disabled-password --gecos "" gh_deploy
sudo usermod -aG docker gh_deploy
echo "[✅] Created user!"


# create ssh keys
mkdir -p /home/gh_deploy/.ssh
chmod 700 /home/gh_deploy/.ssh

ssh-keygen -t ed25519 -C "github-actions" -f /home/gh_deploy/.ssh/github_deploy_key -N ""

cat /home/gh_deploy/.ssh/github_deploy_key.pub >> /home/gh_deploy/.ssh/authorized_keys
chmod 600 /home/gh_deploy/.ssh/authorized_keys
chown -R gh_deploy:gh_deploy /home/gh_deploy/.ssh


echo "=================================================="
echo "⚠️  ACTION REQUIRED  ⚠️"
echo "! copy to github actions secrets"
echo "=================================================="
echo "Set secrets for github actions:"
echo "--------------------"
echo "SSH_KEY:"
cat /home/gh_deploy/.ssh/github_deploy_key
echo "--------------------"
echo "SSH_USER:"
echo "gh_deploy"
echo "--------------------"
echo "SSH_HOST:"
echo "$(curl -s ifconfig.me)"
echo "--------------------"
echo "SSH_PORT:"
echo "<your_ssh_port>"
echo "--------------------"
echo "[✅] Created ssh keys!"
echo ""
read -p "press [ENTER] to continue after adding github actions secrets..."


echo "=================================================="
echo "⚠️  ACTION REQUIRED  ⚠️"
echo "! add deploy key to github repo"
echo "=================================================="
echo "--------------------------------------------------"
cat /home/gh_deploy/.ssh/github_deploy_key.pub
echo "--------------------------------------------------"
echo ""
read -p "press [ENTER] to continue after adding deploy key to github repo..."


eval "$(ssh-agent -s)"
ssh-add /home/gh_deploy/.ssh/github_deploy_key
mkdir -p ~/.ssh
ssh-keyscan github.com >> ~/.ssh/known_hosts


# clone repo & permissions setting
cd /opt/
git clone git@github.com:Anton293/anon-confess--team.git anon-confess
git config --global --add safe.directory /opt/anon-confess
echo "[✅] Cloned Repo!"


POSTGRES_PASSWORD=$(openssl rand -hex 16)
SECRET_KEY=$(openssl rand -hex 32)
echo "[✅] Generated secrets!"


read -p "Enter Postgres username (default: myuser): " INPUT_USER
POSTGRES_USER=${INPUT_USER:-myuser}
echo "[✅] Using Postgres user: $POSTGRES_USER"


# create .env file
cat > /opt/anon-confess/.env <<EOF
APP_ENV=production

POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=anon_db

DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/anon_db
REDIS_URL=redis://redis:6379/0

SESSION_SECRET_KEY=$SECRET_KEY
EOF

echo "[✅] Create .env!"


# set permissions
chown -R gh_deploy:gh_deploy /var/www/demo.harkuhsyn.com/
chown -R gh_deploy:gh_deploy /opt/anon-confess/
echo "[✅] Set permissions gh_deploy:gh_deploy!"


# start docker compose
sudo -u gh_deploy docker-compose -f /opt/anon-confess/docker-compose.yml up -d --build
echo "[✅] Started docker compose!"


echo "[✅] Ready base settings project for ci/cd."
echo ""
read -p "⚠️⚠️⚠️ press [ENTER] to continue after backend is healthy..."
sudo -u gh_deploy docker-compose exec -T backend sh -c "alembic revision --autogenerate -m 'Initial structure'"
sudo -u gh_deploy docker-compose exec -T backend sh -c "alembic upgrade head"

# cleanup
rm /home/gh_deploy/.ssh/github_deploy_key

echo "[🎉] Setup completed successfully!"
