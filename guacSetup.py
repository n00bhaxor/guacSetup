#!/usr/bin/env python3

# Simple script to set up a number of guacamole users
# assigns them passwords via diceware
# and assigns them to an SSH/CLI and Xvnc session
# for Kali Linux

# Todo:
# Make it pretty
# Separate out the functions so that we don't have to run the whole loop just to create a group, e.g.
# do something with the json so we don't need to create a file for every operation.

# Let's import our libraries
import guacapy
import json
import os
import diceware
import argparse
from shutil import rmtree
import sys
from random import randint

# Function to generate a random password using diceware
# Setting default to 5 words separated by a space
# and adding a number at the beginning
def getPassword():
    diceware.config.OPTIONS_DEFAULTS['num']=5
    diceware.config.OPTIONS_DEFAULTS['delimiter'] = '-'
    passphrase = diceware.get_passphrase()
    #passphrase = str(randint(1,1000)) + " " + passphrase
    return passphrase


# Function to check to see if a connection group already exists
def check_group(client,groupName):
    groupInfo = client.get_connection_group_by_name(groupName)
    if groupInfo != None:
        return False
    else:
        return True

# Create Connection Group
def add_group(client,sName,tempDir):
    groupName = sName
    sGroupFile = tempDir + groupName + '-group.json'
    f = open(sGroupFile, "a+")
    f.write('{\n')
    f.write('"parentIdentifier":"ROOT",\n')
    f.write('"name":"' + groupName + '",\n')
    f.write('"type":"ORGANIZATIONAL",\n')
    f.write('"attributes":{"max-connections":"","max-connections-per-user":""}\n')
    f.write('}\n')
    f.close()
    f = open(sGroupFile, "r")
    sgPayload = f.read()
    sgPayload = json.loads(sgPayload)
    newSGroup = client.add_connection_group(sgPayload)
    f.close()
    return


# This function creates a user group, which we'll add users to.
# Makes it easier to modify/delete later.
def add_user_group(client,userGroupName,tempDir):
    userGroupFile = tempDir + userGroupName + '-UserGroup.json'
    f = open(userGroupFile, "a+")
    f.write('{\n')
    f.write('"identifier":"' + userGroupName + '",\n')
    f.write('"attributes":{"disabled": ""}\n')
    f.write('}\n')
    f.close()
    f = open(userGroupFile, "r")
    ugPayload = f.read()
    ugPayload = json.loads(ugPayload)
    newUGroup = client.add_group(ugPayload)
    f.close()
    return

def modify_user_group(client,userGroupName,studentNumber,tempDir):
    userToAdd = userGroupName + "-" + "Student" + "-" + str(studentNumber)
    userGroupModFile = tempDir + userToAdd + '-Mod.json'
    f = open(userGroupModFile, "a+")
    f.write('[{\n')
    f.write('"op":"add",\n')
    f.write('"path":"/",\n')
    f.write('"value":"' + userToAdd + '"\n')
    f.write('}]\n')
    f.close()
    f = open(userGroupModFile, "r")
    ugModPayload = f.read()
    ugModPayload = json.loads(ugModPayload)
    ugMod = client.edit_group_members(userGroupName,ugModPayload)
    f.close()
    return


# This adds a subgroup under the connection group in case
# users have multiple connections
def add_student_group(client,parentGroup, studentNumber,tempDir):
    # First get the group ID of the parent group so we can add our student group as a sub group
    parentGID = get_group_id(client,parentGroup)
    groupName = parentGroup + '-Student-' + str(studentNumber)
    groupFile = tempDir + groupName + '-group.json'
    f = open(groupFile, "a")
    f.write('{\n')
    f.write('"parentIdentifier":"' + parentGID + '",\n')
    f.write('"name":"' + groupName + '",\n')
    f.write('"type":"ORGANIZATIONAL",\n')
    f.write('"attributes":{"max-connections":"","max-connections-per-user":""}\n')
    f.write('}\n')
    f.close()
    f = open(groupFile, "r")
    cgPayload = f.read()
    cgPayload = json.loads(cgPayload)
    newGroup = client.add_connection_group(cgPayload)
    return

# Add a GUI connection (e.g. RDP)
def add_gui_connection(client,studentGroup,studentNumber,xrdpPassword,tempDir,newIPAddr):
    # Get the group ID of the Student's group
    studentGroupParent = studentGroup + '-Student-' + str(studentNumber)
    parentGID = get_group_id(client,studentGroupParent)
    RDPFile = tempDir + studentGroup + 'Student' + '-Kali-GUI-' + str(studentNumber) + '.json'
    f = open(RDPFile, "a")
    f.write('{\n')
    f.write('"name":"' + studentGroup + '-Kali-GUI-' + str(studentNumber) + '",\n')
    f.write('"parentIdentifier":"' + parentGID + '",\n')
    f.write('"protocol":"rdp",\n')
    f.write('"attributes":{"max-connections":"","max-connections-per-user":""},\n')
    f.write('"active-connections":0,\n')
    f.write('"parameters":{\n')
    f.write('  "port":"3389",\n')
    f.write('  "color-depth":"16",\n')
    f.write('  "security":"any",\n')
    f.write('  "password":"' + xrdpPassword + '",\n')
    f.write('  "username":"root",\n')
    f.write('  "hostname":"' + newIPAddr + '"\n')
    f.write('  }\n')
    f.write('}\n')
    f.close()
    f = open(RDPFile, "r")
    connData = f.read()
    connData = json.loads(connData)
    newClient = client.add_connection(connData)
    return

# Add a CLI connection (e.g. SSH)
# We use Kali linux, hence "Kali" in the connection name
def add_cli_connection(client,studentGroup,studentNumber,sshKeyFile,sshKeyPass,tempDir,newIPAddr):
    studentGroupParent = studentGroup + '-Student-' + str(studentNumber)
    parentGID = get_group_id(client,studentGroupParent)
    SSHFile = tempDir + studentGroup + 'Student' + '-Kali-CLI-' + str(studentNumber) + '.json'
    f = open(SSHFile, "a")
    f.write('{\n')
    f.write('"name":"' + studentGroup + '-Kali-CLI-' + str(studentNumber) + '",\n')
    f.write('"parentIdentifier":"' + parentGID + '",\n')
    f.write('"protocol":"ssh",\n')
    f.write('"attributes":{"max-connections":"","max-connections-per-user":""},\n')
    f.write('"active-connections":0,\n')
    f.write('"parameters":{\n')
    f.write('  "port":"22",\n')
    f.write('  "username":"student",\n')
    f.write('  "passphrase":"' + sshKeyPass + '",\n')
    f.write('  "hostname":"' + newIPAddr + '",\n')
    privKeyFile = open(sshKeyFile, "r")
    privKeyData = privKeyFile.read()
    privKeyData = privKeyData.replace("\n", "\\n")
    privKeyData = privKeyData.replace("END RSA PRIVATE KEY-----\\n", "END RSA PRIVATE KEY-----")
    f.write('  "private-key": "' + privKeyData + '"\n')
    f.write('  }\n')
    f.write('}\n')
    f.close()
    f = open(SSHFile, "r")
    connData = f.read()
    connData = json.loads(connData)
    newClient = client.add_connection(connData)
    return

# Add a guacamole user
def add_user(client,groupName,studentNumber,tempDir):
    myStudent = groupName + '-Student-' + str(studentNumber)
    userFile = tempDir + myStudent + ".json"
    newStudent = {}
    newStudent.update({'name': myStudent})
    studentPass = getPassword()
    newStudent.update({'pass': studentPass})

    f = open(userFile, "a")
    f.write("{\n")
    f.write('"username":"' + myStudent + '",\n')
    f.write('"password":"' + studentPass + '",\n')
    f.write('"attributes": {\n')
    f.write('  "disabled": "",\n')
    f.write('  "expired": "",\n')
    f.write('  "access-window-start": "",\n')
    f.write('  "access-window-end": "",\n')
    f.write('  "valid-from": "",\n')
    f.write('  "valid-until": "",\n')
    f.write('  "timezone": ""\n')
    f.write('  }\n')
    f.write('}\n')
    f.close()
    f = open(userFile, "r")
    userData = f.read()
    userData = json.loads(userData)
    client.add_user(userData)
    return newStudent

def save_student_info(infoFile,newStudent):
    sInfo = open(infoFile, "a")
    sInfo.write(newStudent['name'] + "," + newStudent['pass'] + '\n')
    sInfo.close()

def get_conn_id(client,connectionName):
    data = client.get_connection_by_name(connectionName)
    return data['identifier']

def get_group_id(client,groupName):
    data = client.get_connection_group_by_name(groupName)
    groupId = data['identifier']
    return groupId

def get_perms(client,userName):
    perms = client.get_permissions(userName)
    return perms



def assign_perms(client,studentGroup,studentNumber,connectionName,tempDir):

    # We'll need the groupID, connection group ID, and connection ID
    myGroupId = get_group_id(client,studentGroup)
    connGroupName = studentGroup + '-Student-' + str(studentNumber)
    connGroupId = get_group_id(client,connGroupName)
    connId = get_conn_id(client,connectionName)
    myStudent = studentGroup + '-Student-' + str(studentNumber)

    # Check to see if the user already has permissions to the connection group
    # Otherwise the script will error out and quit

    userPerms = get_perms(client,myStudent)
    if connGroupId not in userPerms['connectionGroupPermissions'].keys():
        # First give user permission to the GroupName
        permFile = tempDir + groupName + "-perms.json"
        f = open(permFile, "w")
        f.write('[{\n')
        f.write('"op":"add",\n')
        f.write('"path":"/connectionGroupPermissions/' + myGroupId + '",\n')
        f.write('"value":"READ"\n')
        f.write('}]\n')
        f.close()
        f = open(permFile, "r")
        permData = f.read()
        permData = json.loads(permData)
        client.grant_permission(myStudent, permData)



        # First give the user permissions to the connection Group
        permFile = tempDir + connGroupName + "-perms.json"
        f = open(permFile, "w")
        f.write('[{\n')
        f.write('"op":"add",\n')
        f.write('"path":"/connectionGroupPermissions/' + connGroupId + '",\n')
        f.write('"value":"READ"\n')
        f.write('}]\n')
        f.close()
        f = open(permFile, "r")
        permData = f.read()
        permData = json.loads(permData)
        client.grant_permission(myStudent, permData)
    else:
        print("User already has permissions to the Connection Group. Proceeding with adding permissions to connections.")

    # Now permissions to the connection
    permFile = tempDir + connectionName + "-perms.json"
    f = open(permFile, "w")
    f.write('[{\n')
    f.write('"op":"add",\n')
    f.write('"path":"/connectionPermissions/' + connId + '",\n')
    f.write('"value":"READ"\n')
    f.write('}]\n')
    f.close()
    f = open(permFile, "r")
    permData = f.read()
    permData = json.loads(permData)
    client.grant_permission(myStudent, permData)
    f.close()


def main(groupName,numStudents,ipAddr,outFile,varsFile,guacPort,guacSecure,isHttp,guacUrl,hostsFile):

    # Parse JSON file that has our variables:
    f = open(varsFile, "r")
    myVars = f.read()
    myVars = json.loads(myVars)
    guacamoleAdmin = myVars['guacamoleAdmin']
    guacamoleAdminPass = myVars['guacamoleAdminPass']
    guacamoleServer = myVars['guacamoleServer']
    xrdpPassword = myVars['xrdpPassword']
    sshKeyFile = myVars['sshKeyFile']
    sshKeyPass = myVars['sshKeyPass']
    tempDir = myVars['tempDir']

    # Make our temp directory if it doesnt exist
    os.makedirs(os.path.dirname(tempDir), exist_ok=True)

    # Our client connection
    if isHttp == 'True':
        m = 'http'

    # First add the group or school name to Guacamole. This will store all connections assigned to that group
    checkGroup=check_group(client,groupName)
    if checkGroup == False:
        print("Group exists!! Try a different group name\r\n.")
        exit(1)
    else:
        add_group(client,groupName,tempDir)

    # Create the user group
    add_user_group(client,groupName,tempDir)

    # Enter loop, create users, connection groups and connections for all users.
    studentStart = int(ipAddr.split('.')[3])
    studentMax = studentStart + int(numStudents)

    while studentStart < studentMax:
        studentNum = studentStart

        # Parse the IP address octets
        oct1 = ipAddr.split('.')[0]
        oct2 = ipAddr.split('.')[1]
        oct3 = ipAddr.split('.')[2]
        oct4 = ipAddr.split('.')[3]

        # Assemble the IP address
        newIPAddr = oct1 + '.' + oct2 + '.' + oct3 + '.' + str(studentStart)
        # Create the student Guacamole user name
        newStudent = add_user(client,groupName,studentNum,tempDir)
        save_student_info(outFile,newStudent)

        # Add the student guacamole user to a user group
        modify_user_group(client,groupName,studentNum,tempDir)

        # Add the student connection group
        add_student_group(client,groupName,studentNum,tempDir)

        # Read file of IP addresses if we don't have a consecutive list
        hosts = []
        with open(hostsFile) as file:
            for line in file:
                hosts.append(line.rstrip())

        # add the kali gui and cli connections

        if hosts:
            ipAddr = hosts[int(numStudents) -1]
            add_gui_connection(client,groupName,studentNum,xrdpPassword,tempDir,ipAddr)
            add_cli_connection(client,groupName,studentNum,sshKeyFile,sshKeyPass,tempDir,ipAddr)
        else:

            add_gui_connection(client,groupName,studentNum,xrdpPassword,tempDir,newIPAddr)
            add_cli_connection(client,groupName,studentNum,sshKeyFile,sshKeyPass,tempDir,newIPAddr)

        # Assign permissions to connections
        # First the Kali GUI connection
        connectionName = groupName + '-Kali-GUI-' + str(studentNum)
        assign_perms(client,groupName,studentNum,connectionName,tempDir)

        # Now the Kali CLI connection
        connectionName = groupName + '-Kali-CLI-' + str(studentNum)
        assign_perms(client,groupName, studentNum, connectionName,tempDir)


        studentStart +=1

    # Delete the json files used to create users, groups, and connections.
    # uncomment if you think there's an issue w/ JSON creation
    rmtree(tempDir)
    print("\r\n")
    print("Your Student User passwords have been saved to " + outFile + "\r\n")
    print("PLEASE PROTECT THIS INFORMATION APPROPRIATELY!\r\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Script to set up an existing Guacamole instance.
    The Script will add a user and connection group and connections for each user. Users will only have access
    to their own connections, one CLI and one GUI.""")
    parser.add_argument('-g', '--group-name', dest='groupName', action='store', required=True,
                        help='School or Group name')
    parser.add_argument('-n', '--number', dest='numStudents', action='store', required=True,
                        help='Number of Students'
                        )
    parser.add_argument('-i', '--ip-addr', dest='ipAddr', action='store', required=False, default='10.10.10.10',
                        help='IP Address of the first system you would like Guacamole to connect to')
    parser.add_argument('-o', '--out-file', dest='outFile', action ='store', required=False, default='./userInfo.csv',
                        help='Output File for User Info')
    parser.add_argument('-f', '--vars-file', dest='varsFile', action='store', required=True, default="./guacCreds.json",
                        help='file containing guacamole login info, in JSON format')
    parser.add_argument('-p', '--port', dest='guacPort', action='store', required=False, default=443,
                        help='Port that Guacamole is running on')
    parser.add_argument('-k', '--insecure', dest='guacSecure', action='store', required=False, default='True',
                        help='Do not verify TLS certificate')
    parser.add_argument('-t', '--http', dest='isHttp', action='store', required=False, default='False',
                        help='Use HTTP, not HTTPS, NOT RECOMMENDED')
    parser.add_argument('-u', '--url', dest='guacUrl', action='store', required='False', default='/',
                        help='Guacamole URL if it\'s not in the web root')
    parser.add_argument('-l', '--hosts-file', dest='hostsFile', action='store', required=False,
                        help="File with list of IP addresses for connections")

    args = parser.parse_args()
    groupName = args.groupName
    numStudents = args.numStudents
    ipAddr = args.ipAddr
    outFile = args.outFile
    varsFile = args.varsFile
    guacPort = args.guacPort
    guacSecure = args.guacSecure
    isHttp = args.isHttp
    guacUrl = args.guacUrl
    hostsFile = args.hostsFile

    main(groupName,numStudents,ipAddr,outFile,varsFile,guacPort,guacSecure,isHttp,guacUrl,hostsFile)
