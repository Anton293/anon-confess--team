
```bash
cd /opt/
git clone git@github.com:Anton293/anon-confess--team.git anon-confess
git config --global --add sage.directory /opt/anon-confess
chown -R gh_deploy:gh_deploy /opt/anon-confess
```


### Create file on server /opt/anon-confess/.env

```bash
nano /opt/anon-confess/.env
```

*EXAMLE!!! Replace passwords!!!*

```bash
APP_ENV=production

POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=anon_db

DATABASE_URL=postgresql://myuser:mypassword@postgres:5432/anon_db
REDIS_URL=redis://redis:6379/0

SESSION_SECRET_KEY=...
```


## Create user & add to github

### Setting github actions

```bash
SSH_HOST - хост
SSH_USER - логін (gh_deploy)
SSH_KEY - вміст ~/.ssh/id_rsa
```


### github user

```
sudo adduser --disabled-password --gecos "" gh_deploy
sudo usermod -aG docker gh_deploy
```

### get key for gh_deploy and move to github actions.

*Base instruction: Move github_deploy_key > github actions; Move github_deploy_key.pub > /home/gh_deploy/.ssh/authorized_keys.*

```
ssh-keygen -t ed25519 -C "github-actions" -f ./github_deploy_key
```


### ./github_deploy_key.pub add to file on server:
```
sudo vim /home/gh_deploy/.ssh/authorized_keys
chown -R gh_deploy:gh_deploy /var/www/<name_dir_project_in_nginx>/
```



## Init migration db

### alembic: /backend/src
```bash
alembic revision --autogenerate -m "Initial tables"
```


### Settings NGINX




## Local test
```
cd backend
pip install -r requirements.txt
docker run -d --name postgres --env-file .env -p 5432:5432 -v postgres_data:/var/lib/postgresql/data-test postgres:16
alembic revision --autogenerate -m "Initial"
```