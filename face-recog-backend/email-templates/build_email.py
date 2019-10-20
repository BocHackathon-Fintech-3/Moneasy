def buildEmail(emailType, inputs = {}):
    acceptable_types = ["fraud", "registration", "receipt"]
    if emailType not in acceptable_types:
        return False
    current_time = datetime.now()
    formatting_string = "%H:%M %A, %B %d, %Y"
    if type == "registration":
        formatting_string = "%B %d, %Y"
    timestampStr = current_time.strftime(formatting_string)
    if type == "receipt":
        f=open("receipt.html","r")
        content=f.read()
        f.close()
        parameters = ["receipt_number", "email", "pos_id", "location", "time", "amount"]
    elif type == "registration":
        f=open("registration.html","r")
        content=f.read()
        f.close()
        parameters = []
    for parameter in parameters:
        fullstr = "{{"+parameter+"}}"
        content.replace(fullstr, inputs[parameter])
    return content

