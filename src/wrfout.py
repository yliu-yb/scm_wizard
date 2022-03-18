import netCDF4 as nc
import glob
import datetime
class Wrfoutdata():
    def __init__(self, filefolder):
        filepath = glob.glob(filefolder+"wrfout_*")

        self.df = nc.Dataset(filepath[0])
        self.vars = []
        for var in self.df.variables.keys():
            print(var)
            if self.df.variables[var].dimensions == ('Time', 'bottom_top', 'south_north', 'west_east'):
                self.vars.append(var)
        PH = self.df.variables['PH']
        PHB = self.df.variables['PHB']
        times = self.df.variables['Times']
        self.datetime = []
        for time in times:
            strDatatime = ''
            for b in time:
                strDatatime += bytes.decode(b)
            self.datetime.append(datetime.datetime.strptime(strDatatime, '%Y-%m-%d_%H:%M:%S'))
        self.height = []
        pos_ew = 0
        pos_ns = 0
        for i in range(len(PHB[0][:])-1):
            self.height.append((PHB[0][i][pos_ns][pos_ew] + PH[0][i][pos_ns][pos_ew]) / 9.81 / 1000.)