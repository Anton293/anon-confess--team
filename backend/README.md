
```bash
cd /opt/
git clone git@github.com:Anton293/anon-confess--team.git anon-confess
```


### Create file on server /opt/anon-confess/.env

```bash
nano /opt/anon-confess/.env
```

*EXAMLE!!! Replace passwords!!!*

```bash
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=anon_db

DATABASE_URL=postgresql://myuser:mypassword@postgres:5432/anon_db
REDIS_URL=redis://redis:6379/0

SESSION_SECRET_KEY=...
```



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

### get key for gh_deploy and move to github actions

```
ssh-keygen -t ed25519 -C "github-actions" -f ./github_deploy_key
```


### ./github_deploy_key.pub add to file on server:
```
sudo vim /home/gh_deploy/.ssh/authorized_keys
```

TODO: Settings NGINX