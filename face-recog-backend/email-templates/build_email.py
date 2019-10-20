from datetime import datetime
def buildEmail(emailType, inputs = {}):
    acceptable_types = ["fraud", "registration", "receipt"]
    print(emailType)
    if emailType not in acceptable_types:
        return False
    #current_time = datetime.now()
    #formatting_string = "%H:%M %A, %B %d, %Y"
    #if type == "registration":
        #formatting_string = "%B %d, %Y"
    #timestampStr = current_time.strftime(formatting_string)
    if emailType == "receipt":
        f=open("email-templates/receipt.html","r")
        content=f.read()
        f.close()
        parameters = ["receipt_number", "email", "pos_id", "location", "time", "amount"]
    elif emailType == "registration":
        f=open("email-templates/registration.html","r")
        content=f.read()
        f.close()
        parameters = []
    for parameter in parameters:
        fullstr = "{{"+str(parameter)+"}}"
        content = content.replace(str(fullstr), str(inputs[parameter]))
    return content
