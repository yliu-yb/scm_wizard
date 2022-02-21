import lxml
from lxml import etree
from make_forcing_nc import ForcingNCFileMake
dtd_path = '../../scm_wizard_data/doc/column.dtd'
input_souding_path = '../../scm_wizard_data/data/input_sounding'
input_soil_path = '../../scm_wizard_data/data/input_soil'
force_ideal_path = '../../scm_wizard_data/data/force_ideal.nc'
class Parse_xml():
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.xml_file = lxml.etree.parse(self.xml_path)
    def getLatestError(self):
        if self.error_mk == -1:
            return 'error'
    def validate(self):
        xml_validator = lxml.etree.DTD(file=dtd_path)
        is_valid = xml_validator.validate(self.xml_file)
        return is_valid,xml_validator.error_log
    def make_forcing(self):
        # 获取初始场和强迫场数据
        columns = self.xml_file.getroot()
        column =columns.find('column')
        profile = column.find('profile')
        forcing = profile.find('forcing')
        data_forcing_fromfile = forcing.find('data_forcing_fromfile')
        if data_forcing_fromfile != None:
            forcing_dir = data_forcing_fromfile.get('dir')
            forcing_start_datetime = data_forcing_fromfile.get('start_datetime')
            forcing_end_datetime = data_forcing_fromfile.get('end_datetime')
            forcing_time_resolution = data_forcing_fromfile.get('time_resolution')
            mfn = ForcingNCFileMake()
            isok,log = mfn.make(forcing_dir, forcing_start_datetime, forcing_end_datetime, forcing_time_resolution, force_ideal_path)
            print(isok)
            if isok:
                self.force_datetime = mfn.datetime
                self.force_z = mfn.z
                self.force_u = mfn.u
                self.force_v = mfn.v
                self.force_w = mfn.w
                self.force_qvapor = mfn.qvapor
                self.force_qcloud = mfn.qcloud
                self.force_qrain = mfn.qrain
                self.force_theta = mfn.theta
            return isok,log
    def make_input_sounding(self):
        columns = self.xml_file.getroot()
        column = columns.find('column')
        profile = column.find('profile')
        sounding = profile.find('sounding')
        outline_souding = sounding.find('column_outline_sounding')
        # input_souding第1行数据
        z_terrain = float(outline_souding.find('z_terrain').text)
        u_10 = float(outline_souding.find('u_10').text)
        v_10 = float(outline_souding.find('v_10').text)
        t_2 = float(outline_souding.find('t_2').text)
        q_2 = float(outline_souding.find('q_2').text)
        psfc = float(outline_souding.find('psfc').text)
        # input_sounding第2行以上数据
        sounding_data = sounding.find('data_sounding').text
        sounding_data_list = [float(x) for x in sounding_data.split()]
        z_sounding = sounding_data_list[
                     int(outline_souding.find('z_sounding').get('row')) - 1:len(sounding_data_list):5]
        u_sounding = sounding_data_list[
                     int(outline_souding.find('u_sounding').get('row')) - 1:len(sounding_data_list):5]
        v_sounding = sounding_data_list[
                     int(outline_souding.find('v_sounding').get('row')) - 1:len(sounding_data_list):5]
        theta = sounding_data_list[int(outline_souding.find('theta').get('row')) - 1:len(sounding_data_list):5]
        qv = sounding_data_list[int(outline_souding.find('qv').get('row')) - 1:len(sounding_data_list):5]
        self.souding_z = z_sounding
        self.souding_u = u_sounding
        self.souding_v = v_sounding
        self.souding_theta = theta
        self.souding_qv = qv
        # 输出input_sounding
        with open(input_souding_path, "w") as f:
            f.write(format(z_terrain, '.1f') + ' ' + format(u_10, '.1f') + ' ' + format(v_10, '.1f')
                    + ' ' + format(t_2, '.1f') + ' ' + format(q_2, '.4f') + ' ' + format(psfc, '.1f'))
            f.write('\n')
            for i in range(len(z_sounding)):
                f.write(format(z_sounding[i], '.1f') + ' ' + format(u_sounding[i], '.1f') + ' ' + format(v_sounding[i],
                                                                                                         '.1f')
                        + ' ' + format(theta[i], '.1f') + ' ' + format(qv[i], '.4f'))
                f.write('\n')
        return True
    def make_input_soil(self):
        columns = self.xml_file.getroot()
        column = columns.find('column')
        profile = column.find('profile')
        sounding = profile.find('sounding')
        # input_soil数据信息
        soil = profile.find('soil')
        outline_soil = soil.find('column_outline_soil')
        # input_soil第1行数据
        zero = float(outline_soil.find('zero').text)
        TSK = float(outline_soil.find('TSK').text)
        TMN = float(outline_soil.find('TMN').text)
        # input_soil第2行以上数据
        soil_data = soil.find('data_soil').text
        soil_data_list = [float(x) for x in soil_data.split()]
        z_soil = soil_data_list[int(outline_soil.find('z_soil').get('row')) - 1:len(soil_data_list):3]
        SOILT = soil_data_list[int(outline_soil.find('SOILT').get('row')) - 1:len(soil_data_list):3]
        SOILM = soil_data_list[int(outline_soil.find('SOILM').get('row')) - 1:len(soil_data_list):3]
        # 输出input_soil
        with open(input_soil_path, "w") as f:
            f.write(format(zero, '.7f') + ' ' + format(TSK, '.7f') + ' ' + format(TMN, '.7f'))
            f.write('\n')
            for i in range(len(z_soil)):
                f.write(format(z_soil[i], '.7f') + ' ' + format(SOILT[i], '.7f') + ' ' + format(SOILM[i], '.7f'))
                f.write('\n')
        return True