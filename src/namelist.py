namelist_input_path = './namelist.input'

class Namelist():
    def __init__(self, io):
        self.parameter = []
        self.defaultValue = []
        self.description = []
        self.mainDomain = []
        self.nest = []
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

    def Save(self):
        f = open(namelist_input_path, 'w')
        for i in range(0, len(self.parameter)):
            if str(self.parameter[i]).find('&') != -1:
                if i > 0:
                    f.write('/')
                    f.write('\n')
                line = self.parameter[i]
            else:
                line = str(self.parameter[i]).ljust(40)
                line += ' = '
                if i > 0 and i < 17:
                    line += str(self.mainDomain[i]).zfill(2)
                else:
                    line += str(self.mainDomain[i])
                line += ','

            for nest in self.nest:
                if str(nest[i]) != '':
                    if i > 0 and i < 17:
                        line += str(nest[i]).zfill(2)
                    else:
                        line += nest[i]
                    line += ','

            f.write(line)
            f.write('\n')
        f.write('/')
        f.close()
        return namelist_input_path