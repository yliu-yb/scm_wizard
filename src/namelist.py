
class Namelist():
    def __init__(self, io):
        self.parameter = []
        self.defaultValue = []
        self.description = []
        self.mainDomain = []
        if io == 0:
            self.GetPara_DefaultValue_Descrip()
            self.mainDomain = self.defaultValue
        elif io == 1:
            self.GetFromUserSetNamelistFile()

    def GetPara_DefaultValue_Descrip(self):
        f = open('namelist_para_defaultValue_description.intput', 'r')
        lines = f.readlines()
        for line in lines:
            strs = line.split(';',2)
            if(strs[0] == '\n'):
                continue
            self.parameter.append(strs[0])
            self.defaultValue.append(strs[1])
            self.description.append(strs[2])
        f.close()

    def GetFromUserSetNamelistFile(self):
        return 0