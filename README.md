# Imouto

## Information
----------
Imouto is an IRC bot which will organize the answers from users to a specified question into
files representing the hour of answering.

For instance:

```
<10:34:55> <userA> what is up userB?
<10:35:20> <userB> trying to sleep
```
Imouto will then add *"trying to sleep"* to *"answerpath/userB/10.txt"*

If there is one or more answers in the file, imouto will message the channel a randomized answer.


```
<10:34:55> <userA> 	what's happening userB?
<10:34:55> <botnick> userB is doing this: working on my irc bot
<10:35:20> <userB> 	trying to sleep
```

## Usage
----------
To start the bot, type
```
python3 Imouto.py server[:port] #channel nick [configpath]
```

You will probably need to espace the *"#"* char.
Check the exampleconfig.ini to see how the config is to be used.

After the bot is up and running for the first time, type
```
/msg botnick addallinchannel
```
 and it will add everyone currently in the channel used.
For more information about how the commands work, check the code or msg the bot

```
/msg botnick help
```

## Requirements
----------
https://bitbucket.org/jaraco/irc

Python3 or higher
