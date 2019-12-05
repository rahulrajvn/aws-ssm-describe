import boto3
session = boto3.Session(profile_name='XXXXXXXXXX')
ssm_cli = session.client('ssm', region_name = 'eu-west-1')

import datetime
import csv
time = datetime.datetime.now().strftime ('%Y-%m-%d-%H-%M-%S')
filename_describe_ssm= ('Describe_SSM_eu-west-1_XXXXXXX' + time + '.csv')

fieldnames =['Instances_id' , 'PingStatus', 'LastPingDateTime', 'AgentVersion', 'IsLatestVersion',
            'PlatformType', 'PlatformName', 'PlatformVersion' , 'ResourceType', 'IPAddress',
            'ComputerName', 'AssociationStatus', 'LastSuccessfulAssociationExecutionDate',
            'CISCO_XXXXX', 'Symantec_XXXXX', 'Domain_Joined', 'Instance_KB_Installed', 'Instance_OtherKB_Installed',
            'Instance_KB_Missing' , 'Instance_KB_Failed', 'uniqInstalled_KBs', 'Missing_KBs']

response_ssm_describe_instance = ssm_cli.describe_instance_information()

with open(filename_describe_ssm, 'w', newline='') as csvFile:
    writer = csv.writer(csvFile, dialect='excel')
    writer.writerow(fieldnames)

    while True:
        for ssm_managed_instances in response_ssm_describe_instance ['InstanceInformationList']:
    #    print(ssm_managed_instances)
            ssm_managed_instances_id = ssm_managed_instances['InstanceId']
            print(ssm_managed_instances_id)
            ssm_managed_instances_pingstatus = ssm_managed_instances['PingStatus'],
            ssm_managed_instances_lastping = ssm_managed_instances['LastPingDateTime'].date()
            ssm_managed_instances_agentversion = ssm_managed_instances['AgentVersion']
            ssm_managed_instances_islatestversion = ssm_managed_instances['IsLatestVersion']
            ssm_managed_instances_platformtype = ssm_managed_instances['PlatformType']
            ssm_managed_instances_platformname = ssm_managed_instances['PlatformName']
            ssm_managed_instances_platformversion = ssm_managed_instances['PlatformVersion']
            ssm_managed_instances_resourcetype = ssm_managed_instances['ResourceType']
            ssm_managed_instances_ip = ssm_managed_instances['IPAddress']
            ssm_managed_instances_compname = ssm_managed_instances['ComputerName']
            try:
                ssm_managed_instances_assos_status = ssm_managed_instances['AssociationStatus']
                ssm_managed_instances_lastsuccssassoc_date = ssm_managed_instances['LastSuccessfulAssociationExecutionDate']
            except Exception as e:
                ssm_managed_instances_assos_status = "Not_Applicable"
                ssm_managed_instances_lastsuccssassoc_date = "Not_Applicable"
                print(e)


            ssm_managed_instances_inventory_CISCO = False
            ssm_managed_instances_inventory_AV = False
            ssm_managed_instances_inventory_domainjaoin = False


            ssm_managed_instances_inventory = ssm_cli.list_inventory_entries( InstanceId= ssm_managed_instances_id , TypeName='AWS:Application')
            #print(ssm_managed_instances_inventory)
            count = 0
            while True:
                for instance_entry in ssm_managed_instances_inventory['Entries']:
                    count = count + 1
                    instance_entry_str = str(instance_entry)
                    if instance_entry_str.find("Cisco XXXX for Endpoints Connector") != -1:
                        ssm_managed_instances_inventory_CISCO = True
                    if instance_entry_str.find("Symantec XXXXXX") != -1:
                        ssm_managed_instances_inventory_AV = True
                    if ssm_managed_instances_compname.find("XXXXX.local") != -1:
                        ssm_managed_instances_inventory_domainjaoin = True
                try :
                    if ssm_managed_instances_inventory.get('NextToken','NULL') != 'NULL':
                            ssm_managed_instances_inventory = ssm_cli.list_inventory_entries( InstanceId= ssm_managed_instances_id , TypeName='AWS:Application' , NextToken = ssm_managed_instances_inventory.get('NextToken','NULL'))
                    else:
                        break
                except Exception as e:
                    print(e)




            ################################
            ##Checking out KB Counts
            Instance_KB_Installed = Instance_OtherKB_Installed = Instance_KB_Missing = Instance_KB_Failed = 0
            ssm_instance_patchestat = ssm_cli.describe_instance_patch_states( InstanceIds=[ ssm_managed_instances_id] )
            try:
                Instance_KB_Installed = str(ssm_instance_patchestat['InstancePatchStates'][0]['InstalledCount'])
                Instance_OtherKB_Installed = str(ssm_instance_patchestat['InstancePatchStates'][0]['InstalledOtherCount'])
                Instance_KB_Missing = str(ssm_instance_patchestat['InstancePatchStates'][0]['MissingCount'])
                Instance_KB_Failed = str(ssm_instance_patchestat['InstancePatchStates'][0]['FailedCount'])
                print(Instance_KB_Installed, Instance_OtherKB_Installed , Instance_KB_Missing, Instance_KB_Failed)
            except Exception as e:
                Instance_KB_Installed = Instance_OtherKB_Installed = Instance_KB_Missing = Instance_KB_Failed = 0
                print(e)
            ################################
            ##Checking out Missing Kb's
            Installed_KBs = []
            Missing_KBs =[]
            ssm_instance_patches = ssm_cli.describe_instance_patches( InstanceId= ssm_managed_instances_id )
            while True:
                for kbs in ssm_instance_patches['Patches']:
                    #print(kbs)
                    #print(kbs['KBId'] ,kbs['Classification'], kbs['Severity'] , kbs['State']  )
                    if kbs['State'] == 'Installed':
                        Installed_KBs.append(kbs['KBId'])
                    elif kbs['State'] == 'Missing':
                        Missing_KBs.append(kbs['KBId'])
                try :
                    if ssm_instance_patches.get('NextToken','NULL') != 'NULL':
                        ssm_instance_patches = ssm_cli.describe_instance_patches( InstanceId= ssm_managed_instances_id , NextToken = ssm_instance_patches.get('NextToken','NULL'))
                    else:
                        break
                except Exception as e:
                    print(e)

            ################################
            ## Checking out installed KB's
            WINUPInstalled_KBs = []
            ssm_managed_instances_inventory = ssm_cli.list_inventory_entries( InstanceId= ssm_managed_instances_id , TypeName='AWS:WindowsUpdate')
            while True:
                for kbs in ssm_managed_instances_inventory['Entries']:
                    #print(kbs['HotFixId'])
                    WINUPInstalled_KBs.append(kbs['HotFixId'])
                #break

                count = 0

                #print(ssm_managed_instances_inventory.get('NextToken','NULL'))
                try :
                    if ssm_managed_instances_inventory.get('NextToken','NULL') != 'NULL':
                        ssm_managed_instances_inventory = ssm_cli.list_inventory_entries( InstanceId= ssm_managed_instances_id , TypeName='AWS:WindowsUpdate' , NextToken = ssm_managed_instances_inventory.get('NextToken','NULL'))
                    else:
                        break
                except Exception as e:
                    print(e)

            uniqInstalled_KBs = list(set().union(WINUPInstalled_KBs, Installed_KBs))
            ################################

            raw = [ssm_managed_instances_id , ssm_managed_instances_pingstatus,
            ssm_managed_instances_lastping, ssm_managed_instances_agentversion,
            ssm_managed_instances_islatestversion , ssm_managed_instances_platformtype ,
            ssm_managed_instances_platformname , ssm_managed_instances_platformversion ,
            ssm_managed_instances_resourcetype , ssm_managed_instances_ip ,
            ssm_managed_instances_compname , ssm_managed_instances_assos_status ,
            ssm_managed_instances_lastsuccssassoc_date , ssm_managed_instances_inventory_CISCO,
            ssm_managed_instances_inventory_AV , ssm_managed_instances_inventory_domainjaoin,
              Instance_KB_Installed,Instance_OtherKB_Installed,Instance_KB_Missing, Instance_KB_Failed,
                 uniqInstalled_KBs, Missing_KBs ]

            writer.writerow(raw)


        try:
            if response_ssm_describe_instance.get('NextToken','NULL') != 'NULL':
                response_ssm_describe_instance = ssm_cli.describe_instance_information(NextToken = response_ssm_describe_instance.get('NextToken','NULL'))
            else:
                break
        except Exception as e:
            print(e)

csvFile.close()
print("Completed")
