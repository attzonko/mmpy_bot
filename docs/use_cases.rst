Use cases
=========

Standard cases for web organizations.


Support | QA
------------

``callto John|Alex|All Your text ...`` - Emergency call

``smsto John|Alex|All Your text ...`` - Emergency sms

``task|bug|feature @username <low|normal|default|high|urgent> Task subject ...\nDescription`` - create task on bug tracker/etc

``contact info <@username>`` - Show everyone's/username emergency contact info

``remind me to TEXT at|on|in TIME`` - Set a reminder for a thing, at a time

``remind @user1,@user2 to TEXT at|on|in TIME`` - Set a reminder for a thing, at a time for somebody else


Development
-----------

**Standard**

``build VERSION`` - Run build

``test CURRENT|COMMIT`` - Run tests


**Stage servers**

``ls`` - List all available staging servers

``make COMMIT <fake> or <-1h|d>`` - Create stage server. optional: hour|day ago

``rm ID`` - Remove server by ID


DevOps
------

**Standard**

``maintenance on|off`` - Show maintenance page on website


**AWS**

``ls ami server1|server2|all`` - Show aws AMI's

``make ami server1|server2`` - Create a new ami

``upgrade|downgrade server1|server2|all <ami>`` - upgrade|downgrade AMI's

``stop upgrade|downgrade`` - Stop upgrade|downgrade


**Distributed version control system**

``update|rollback server1|server2|all <commit>`` - Update code on servers

``stop update|rollback`` - Stop update|rollback


**Configuration management system**

``cms update repo`` - Update own repository (such git pull)

``cms update server1|sever2|all`` - Run server provision (e.g. puppet/chef/ansible)


Internal commands for Bot
-------------------------

``version`` - Get current revision and matterbot version

``selfupdate`` - Update bot and plugins from your CVS repo

``busy`` - Get num of busy workers. Used for monitoring and for check before update

``uptime`` - MatterBot uptime

``ping`` - Ping bot and waiting ``pong``



Everything is limited only by your imagination :)
