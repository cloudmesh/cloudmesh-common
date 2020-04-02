# local ssh test

THis tests checks how fast you can login into your own machine and use
ssh to execute a command.

For this test to work youhave to add your own public key to 

    ~/.ssh/authorized_keys
    
Then use ssh-add

    ssh-add
    
than you can say 

    pytest -v --capture=no tests/2_local
    
This may not work on windows initially or osx as sshd is either not
available or enabled.

## OSX

    go to configuration
    authenticate
    check on Remote Login
    
After you ar e done with it uncheck so your machine is more secure

## Linux

you find out and provide documentation

## Windows 10

you find out and provide documentation
