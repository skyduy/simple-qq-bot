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

- Then install the package used in python:

change directory into simple-qq-bot by `cd simple-qq-bot`

install the package by `pip install -r requirements.txt`

## How to run

- Create database and create user with privilege.
- Modify some settings in config.py
- run the two commands `perl x.pl` and `python qq_bot.py` respectively


## Acknowledgement

 - Fork from [ihciah](https://github.com/ihciah/simple-qq-bot).
 - Based on [Flask](https://github.com/mitsuhiko/flask) and [Mojo-Webqq](https://github.com/sjdy521/Mojo-Webqq/)

## Why this?
 - Simplified functional: support only for group chat.
 - Consistent with the project [wechat](https://github.com/skyduy/wechat)
