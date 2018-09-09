# vmsgSelector
Text selector from VMSG export format - can be use when backuping or migrating selected SMS between mobile phones

1) Open the "inputFile=sms.vmsg" or stdin
2) Select all SMS of phone numbers in "phoneNumber_interest_list"
3) Remove SMS duplicities
4) Optionally remove the small ones (SMS shorter then "iRemoveSmallerThen" ... def = 12)
5) Optionally output split into files with limited about of SMS ("outputFileMaxMsg", default 40 000)

Setup it in the section "#CONFIG" (at the begining of the script).
