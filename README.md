# guacSetup
Script we use for enrichMinds to set up user connection groups in Guacamole.

This is a customized script we use to set up our Guacamole connections for students.
There is an overall connection group for the school/institution we're teaching at,
and a connection sub-group for each student. This way we can control what students
have access to, and we can keep the horseplay to a minimum, because kidz gonna kid.

This script will create both a CLI and GUI connection to Kali Linux. Since we don't
always need a GUI, we can cut back on bandwidth resources whenever possible.

We also use diceware to generate passwords for the students. Feel free to change this
if you want, but we think it's a good way to get the students used to the idea of
having/generating long passphrases (Yes, password managers are awesome, and we
talk to the students about using them, but they may not have access to them from
devices managed by EDUs, and they may not have access to/be able to use cell phones
in class).

User name and passphrase output is written to a file in the clear. Store this info
appropriately. Suggest wiping the file once the students have their passphrases,
and you've got an encrypted backup. Maybe I'll add a function to encrypt with
a passphrase at some point.

You'll need to create a creds file, in JSON format. See the example_json.json for
basic formatting. Just replace the items to the right of the colon for each variable.
The script will take an argument, -v and the file name (yes I just realized that this 
needs to change b/c every other program on this earth uses that to specify verbose).
The script will use a default guacCreds.json if you don't specify one.

At some point I need to separate out the functions so they're not all dependent on each
other, make the output pretty, and add other connection types.

usage: guacSetup.py [-h] -g GROUPNAME -n NUMSTUDENTS -i IPADDR [-o OUTFILE] -v
                    VARSFILE
                    
python3 guacSetup.py -g MySchoolGroup -n 20 -i 10.100.1.10 -v guacCreds.json

This will add a Connection Group called MySchoolGroup with 20 connection sub-groups
for consecutive subnets 10.100.1.10-10.100.20.10, one per student. It will create 20
users in Guacamole. each with a different diceware password. It will use the guacCreds.json
file to load your Guacamole server information. It will save user login info to userInfo.csv.


