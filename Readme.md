# Simple QQ chat bot

## How to install

- Frist install `Mojo-Webqq`

```shell
cpan -i App::cpanminus
# If the command above is too slow, try to use http://mirrors.163.com/.help/cpan.html
cpanm -v Mojo::Webqq
```

  If you run `perl x.pl` and see error about `@INC`, try add these thing in your `.bashrc` or `.zshrc`, whatever.
```shell
PATH="/home/your_username/perl5/bin${PATH+:}${PATH}"; export PATH;
PERL5LIB="/home/your_username/perl5/lib/perl5${PERL5LIB+:}${PERL5LIB}"; export PERL5LIB;
PERL_LOCAL_LIB_ROOT="/home/your_username/perl5${PERL_LOCAL_LIB_ROOT+:}${PERL_LOCAL_LIB_ROOT}"; export PERL_LOCAL_LIB_ROOT;
PERL_MB_OPT="--install_base \"/home/your_username/perl5\""; export PERL_MB_OPT;
PERL_MM_OPT="INSTALL_BASE=/home/your_username/perl5"; export PERL_MM_OPT;
```

- Then install `mysql`, `Flask`, `memcached`, `python-memcached`, `jieba`

```shell
sudo apt-get install mysql-server python-pip memcached python-dev mysql-client libmysqld-dev
sudo pip install Flask python-memcached jieba MySQL-python
# If some problems caused by the internet happen, you can retry several times.
```

## How to run

- Create database and import `database.sql` to mysql
- Create user and grant privilege if you want it more safe, or just use mysql's root account for convenience
- Modify some settings in config.py
- `perl x.pl` and then `python qq_bot.py` in two terminal or use `screen` or `nohup` to run then in background

## Feathers

- Simple learning / replying, maybe some real intelligent things in the future
- Management
- Block/unblock user/group/word
- Small games

## Why this?

- For some fun when there's a bot in a group
- Rewrite a qqbot similar written by me several years ago.
Some volunteers submitted their advices and some even gave me a well-designed report at that time,
but I didn't have some basic knowledge and time to do these things.

    Now I rewrite it in two days and make it open-source.
Though this is not a well-written code,
I hope there are still some enthusiasts build this together.

## Acknowledgement

- Inspired by QQ515912540 and [StoneMoe](https://github.com/StoneMoe/TQ-Bridge-Lite)
- Based on [Flask](https://github.com/mitsuhiko/flask) and [Mojo-Webqq](https://github.com/sjdy521/Mojo-Webqq/)
