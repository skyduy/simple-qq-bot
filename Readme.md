# Simple QQ chat bot

## Install
- Frist install `Mojo-Webqq`

```shell
cpan -i App::cpanminus
# If the command above is too slow, try to use http://mirrors.163.com/.help/cpan.html
cpanm -v Mojo::Webqq
```

- Then install `mysql`, `Flask`, `memcached`, `python-memcached`, `jieba`

```shell
sudo apt-get install mysql-server python-pip memcached python-dev mysql-client libmysqld-dev
sudo pip install Flask python-memcached jieba MySQL-python
# If some problems caused by the internet happen, you can retry several times. 
```

## Run

- Create database and import `database.sql` to mysql
- Create user and grant privilege if you want it more safe, or just use mysql's root account for convenience
- Modify some settings in config.py
- `perl x.pl` and then `python qq_bot.py` in two terminal or use `screen` or `nohup` to run then in background


## Functions

- Simple learning / replying, maybe some real intelligent things in the future
- Management
- Query
- Block / unblock user / group

## Why this?

- For some fun when there's a bot in a group
- Rewrite a qqbot similar written by me several years ago. 
Some volunteers submitted their advices and some even gave me a well-designed report at that time, 
but I didn't have some basic knowledge and time to do these things. 

    Now I rewrote it in 2 days and make it open-source. 
Though this is not a well-written code, 
I hope there are still some enthusiasts build this together.

## Acknowledge

- Inspired by [StoneMoe](https://github.com/StoneMoe/TQ-Bridge-Lite) and QQ515912540