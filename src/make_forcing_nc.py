import netCDF4
import numpy
from netCDF4 import Dataset
from pvlib import atmosphere as atmo
import time
import os
cdlFName = '../doc/forcing_file_2.cdl'

class ForcingNCFileMake():
    def split(self, word):
        return [char for char in word]
    def make(self, reanalyze_nc_data_file, start_datetime, end_datetime, timeresolution, output_path):
        reanalyze_data = Dataset(reanalyze_nc_data_file)
        # 再分析资料日期时间，时间戳
        reanalyze_time = reanalyze_data.variables['time']
        reanalyze_datetime = netCDF4.num2date(reanalyze_time[:], reanalyze_time.units, reanalyze_time.calendar)
        reanalyze_timestamp = [time.mktime(time.strptime(str(x), "%Y-%m-%d %H:%M:%S")) for x in reanalyze_datetime]
        reanalyze_datetime_wrf_format = [time.strftime("%Y-%m-%d_%H:%M:%S", time.strptime(str(x), "%Y-%m-%d %H:%M:%S")) for x in reanalyze_datetime]
        # 开始日期时间和结束日期时间转时间戳
        start_timestamp = time.mktime(time.strptime(start_datetime, "%Y-%m-%d_%H:%M:%S"))
        end_timestamp = time.mktime(time.strptime(end_datetime, "%Y-%m-%d_%H:%M:%S"))
        #检查 再分析资料日期时间是否满足用户设置
        iter_num = int((end_timestamp - start_timestamp) / (float(timeresolution) * 3600))
        reanalyze_missing_datatime = []
        for i in range(iter_num):
            if start_timestamp + i * 3600 not in reanalyze_timestamp:
                reanalyze_missing_datatime.append(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(start_timestamp + i * 3600)))
        if len(reanalyze_missing_datatime) > 0:
            print('reanalyze data missing datetime:')
            print(reanalyze_missing_datatime)
            return False, '再分析资料缺失以下日期'+str(reanalyze_missing_datatime)
        #获得再分析资料数据
        for var in reanalyze_data.variables:
            if var == 'level':
                pressure = reanalyze_data.variables[var]
                alt = [atmo.pres2alt(x * 100) for x in pressure]
            if var == 'u':
                u = reanalyze_data.variables[var][:,:,0,0]
            if var == 'v':
                v = reanalyze_data.variables[var][:,:,0,0]
            if var == 'w':
                w = reanalyze_data.variables[var][:,:,0,0]
            if var == 'q':
                qvapor = reanalyze_data.variables[var][:,:,0,0]
            if var == 'clwc':
                qcloud = reanalyze_data.variables[var][:,:,0,0]
            if var == 'crwc':
                qrain = reanalyze_data.variables[var][:,:,0,0]
            if var == 't':
                temperature = reanalyze_data.variables[var][:,:,0,0]
                xishu = (1000/numpy.array(pressure))**0.286
                theta = [(numpy.array(x) * xishu).tolist() for x in temperature]
        alt.reverse()
        alt = [x - alt[0] for x in alt]
        default_data = [0. for x in alt]
        self.datetime = reanalyze_datetime_wrf_format
        self.z = alt
        # print(self.z)
        self.u = []
        self.v = []
        self.w = []
        self.qvapor = []
        self.qcloud = []
        self.qrain = []
        self.theta = []
        # 更改层数
        z_top = 9417
        z_top_idx = 0
        for i in range(len(alt)):
            if alt[i] > z_top:
                z_top_idx = i + 1 + 4
                break
        print(z_top_idx)
        z_top_idx = 36
        # force_nc.createDimension('force_layers', z_top_idx + 1)
        # 通过cdl生成force_ideal.nc
        os.system("ncgen -o " + output_path + " " + cdlFName)
        print(output_path)
        print(cdlFName)
        # 将再分析资料数据写入force_ideal.nc中
        force_nc = Dataset(output_path, 'r+')

        for itime in range(len(reanalyze_datetime_wrf_format)):
            self.u.append(u[itime][::-1])
            self.v.append(v[itime][::-1])
            self.w.append(w[itime][::-1])
            self.qvapor.append(qvapor[itime][::-1])
            self.qrain.append(qrain[itime][::-1])
            self.qcloud.append(qcloud[itime][::-1])
            self.theta.append(theta[itime][::-1])

            force_nc.variables['Times'][itime] = self.split(reanalyze_datetime_wrf_format[itime])
            # force_nc.variables['Z_FORCE'][itime] = self.z[0:z_top_idx]
            # force_nc.variables['U'][itime] = self.u[itime][0:z_top_idx]
            # force_nc.variables['V'][itime] = self.v[itime][0:z_top_idx]
            # force_nc.variables['W'][itime] = self.w[itime][0:z_top_idx]
            # force_nc.variables['QVAPOR'][itime] = self.qvapor[itime][0:z_top_idx]
            # force_nc.variables['QCLOUD'][itime] =self.qcloud[itime][0:z_top_idx]
            # force_nc.variables['QRAIN'][itime] = self.qrain[itime][0:z_top_idx]
            # force_nc.variables['T'][itime] = self.theta[itime][0:z_top_idx]
            #
            # force_nc.variables['U_G'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['V_G'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['W_SUBS'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['TH_UPSTREAM_X'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['TH_UPSTREAM_Y'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['QV_UPSTREAM_X'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['QV_UPSTREAM_Y'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['U_UPSTREAM_X'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['U_UPSTREAM_Y'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['V_UPSTREAM_X'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['V_UPSTREAM_Y'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['Z_FORCE_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['U_G_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['V_G_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['W_SUBS_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['TH_UPSTREAM_X_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['TH_UPSTREAM_Y_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['QV_UPSTREAM_X_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['QV_UPSTREAM_Y_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['U_UPSTREAM_X_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['U_UPSTREAM_Y_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['V_UPSTREAM_X_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['V_UPSTREAM_Y_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['TAU_X'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['TAU_X_TEND'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['TAU_Y'][itime] = default_data[0:z_top_idx]
            # force_nc.variables['TAU_Y_TEND'][itime] = default_data[0:z_top_idx]
            force_nc.variables['Z_FORCE'][itime] = self.z
            force_nc.variables['U'][itime] = self.u[itime]
            force_nc.variables['V'][itime] = self.v[itime]
            force_nc.variables['W'][itime] = self.w[itime]
            force_nc.variables['QVAPOR'][itime] = self.qvapor[itime]
            force_nc.variables['QCLOUD'][itime] = self.qcloud[itime]
            force_nc.variables['QRAIN'][itime] = self.qrain[itime]
            force_nc.variables['T'][itime] = self.theta[itime]

            force_nc.variables['U_G'][itime] = default_data
            force_nc.variables['V_G'][itime] = default_data
            force_nc.variables['W_SUBS'][itime] = default_data
            force_nc.variables['TH_UPSTREAM_X'][itime] = default_data
            force_nc.variables['TH_UPSTREAM_Y'][itime] = default_data
            force_nc.variables['QV_UPSTREAM_X'][itime] = default_data
            force_nc.variables['QV_UPSTREAM_Y'][itime] = default_data
            force_nc.variables['U_UPSTREAM_X'][itime] = default_data
            force_nc.variables['U_UPSTREAM_Y'][itime] = default_data
            force_nc.variables['V_UPSTREAM_X'][itime] = default_data
            force_nc.variables['V_UPSTREAM_Y'][itime] = default_data
            force_nc.variables['Z_FORCE_TEND'][itime] = default_data
            force_nc.variables['U_G_TEND'][itime] = default_data
            force_nc.variables['V_G_TEND'][itime] = default_data
            force_nc.variables['W_SUBS_TEND'][itime] = default_data
            force_nc.variables['TH_UPSTREAM_X_TEND'][itime] = default_data
            force_nc.variables['TH_UPSTREAM_Y_TEND'][itime] = default_data
            force_nc.variables['QV_UPSTREAM_X_TEND'][itime] = default_data
            force_nc.variables['QV_UPSTREAM_Y_TEND'][itime] = default_data
            force_nc.variables['U_UPSTREAM_X_TEND'][itime] = default_data
            force_nc.variables['U_UPSTREAM_Y_TEND'][itime] = default_data
            force_nc.variables['V_UPSTREAM_X_TEND'][itime] = default_data
            force_nc.variables['V_UPSTREAM_Y_TEND'][itime] = default_data
            force_nc.variables['TAU_X'][itime] = default_data
            force_nc.variables['TAU_X_TEND'][itime] = default_data
            force_nc.variables['TAU_Y'][itime] = default_data
            force_nc.variables['TAU_Y_TEND'][itime] = default_data

        return True,'强迫场文件生成完成'+ output_path
