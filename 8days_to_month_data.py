import os
import re
import glob
import datetime
import numpy as np
from osgeo import gdal
import pprint


class RasterTiff:
    gdal.AllRegister()

    def read_img(self, filename):
        """读取栅格文件"""
        dataset = gdal.Open(filename)
        im_width = dataset.RasterXSize  # 获取栅格文件的宽度
        im_height = dataset.RasterYSize  # 获取栅格文件的高度
        im_bands = dataset.RasterCount  # 获取栅格文件的波段

        im_geotrans = dataset.GetGeoTransform()  # 获取栅格文件的地理坐标系
        im_proj = dataset.GetProjection()  # 获取栅格文件的栅格坐标系
        im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 从栅格文件左上角开始，按照宽度和高度读取栅格文件

        print(type(im_data), im_data.shape)

        del dataset
        return im_height, im_width, im_bands, im_geotrans, im_proj, im_data

    def write_img(self, filename, im_geotrans, im_proj, im_data):
        """写入栅格文件"""
        if 'int8' in im_data.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in im_data.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32

        if len(im_data.shape) == 3:
            im_bands, im_height, im_width = im_data.shape
        else:
            im_bands, (im_height, im_width) = 1, im_data.shape

        drive = gdal.GetDriverByName('GTiff')
        dataset = drive.Create(filename, im_width, im_height, im_bands, datatype)

        dataset.SetGeoTransform(im_geotrans)
        dataset.SetProjection(im_proj)

        if im_bands == 1:
            dataset.GetRasterBand(1).WriteArray(im_data)  # 写入数组数据
        else:
            for i in range(0, im_bands):
                dataset.GetRasterBand(i + 1).WriteArray(im_data)

        del dataset


def month_statistics(year_para, month_para):
    """处理月数据"""
    first_day_month = datetime.date(year_para, month_para, day=1)
    if month_para == 12:
        first_day_next_month = datetime.date(year_para+1, month=1, day=1)
    else:
        first_day_next_month = datetime.date(year_para, month=month_para+1, day=1)
    days_of_month = (first_day_next_month - first_day_month).days
    # 返回当月第一天，下个月第一天，这个月的天数
    return first_day_month, first_day_next_month, days_of_month


lai_8days_folder_path = r'E:\LAI'
for year_index in os.listdir(lai_8days_folder_path):
    lai_8days_year_folder_path = os.path.join(lai_8days_folder_path, year_index)
    lai_paths = sorted(glob.glob(os.path.join(lai_8days_year_folder_path, '*.tif')))
    for month_index in range(1, 13):
        month_list = []
        print(f"{year_index}-{month_index:02}")
        # 检查是否有文件数据
        if not lai_paths:
            print(f"No data found for {year_index}-{month_index:02}")
            continue
        for lai_path in lai_paths:
            # 获取文件名中的日期信息
            name = re.findall(r'GLASS01B01.V60.A(\d{7})', os.path.basename(lai_path))[0]
            date = datetime.datetime.strptime(name, '%Y%j')
            year_int, month_int, day_int = date.year, date.month, date.day
            # year_str, month_str, day_str = str(year_int), str(month_int).zfill(2), str(day_int).zfill(2)
            if month_int == month_index:
                # 同一年相同月份的影响存放在一起，并插入各景影像数据在各月份所占权重
                # 根据所占月份时间长短来确定权重（设为1）
                month_list.append(([lai_path, 1.0]))
        # 检查每月第一天的日期
        # 在使用索引位置之前检查列表是否为空
        if not month_list:
            print("No files found for this month.")
            continue
        else:
            name_month_first = re.findall(r'GLASS01B01.V60.A(\d{7})', os.path.basename(month_list[0][0]))[0]
            date_month_first = datetime.datetime.strptime(name_month_first, '%Y%j')
            # 如果当月第一景数据不是从第1日开始，则加入上一景数据啊
            if date_month_first.day != 1:
                # 往前推8天找到上一景
                date_last_month = date_month_first - datetime.timedelta(days=8)
                # 将前8天的日期数据做格式化，变为字符串
                name_last_month = datetime.datetime.strftime(date_last_month, '%Y%j')
                # 在影像列表中查找并插入上个月最后一景的数据
                for lai_path_sup in lai_paths:
                    path_sup = re.findall(r'GLASS01B01.V60.A(\d{7})', os.path.basename(lai_path_sup))[0]
                    if path_sup == name_last_month:
                        month_list.insert(0, [lai_path_sup, 1.0])

            # 为每月首尾可能跨月影像分配权重
            name_month_list_first = re.findall(r'GLASS01B01.V60.A(\d{7})', os.path.basename(month_list[0][0]))[0]
            name_month_list_last = re.findall(r'GLASS01B01.V60.A(\d{7})', os.path.basename(month_list[-1][0]))[0]
            date_month_list_first = datetime.datetime.strptime(name_month_list_first, '%Y%j')
            date_month_list_last = datetime.datetime.strptime(name_month_list_last, '%Y%j')
            # 获取每月首尾影像的年月日
            year_month_list_first, month_month_list_first, day_month_list_first = date_month_list_first.year, date_month_list_first.month, date_month_list_first.day
            year_month_list_last, month_month_list_last, day_month_list_last = date_month_list_last.year, date_month_list_last.month, date_month_list_last.day
            # 判断首景影响是否属于上月跨月影像（判断是否从1日开始）
            if day_month_list_first != 1:
                # 跨月影像，获取上个月第一天、最后一天、天数
                first_day_month, last_day_month, days_month = month_statistics(year_month_list_first, month_month_list_first)
                last_day_month_datetime = datetime.datetime.strptime(str(last_day_month), '%Y-%m-%d')
                # 求首景影像（跨月）在上个月所占天数
                delta_last_month_last = (last_day_month_datetime-date_month_list_first).days + 1
                # 分配首景影像（跨月）在当前月所占天数，并分配权重
                delta_this_month_first = 8 - delta_last_month_last
                month_list[0][1] = delta_this_month_first / 8
            # 当年当月第一天/最后一天/天数
            first_day_this_month, last_day_this_month, days_this_month = month_statistics(int(year_index), month_index)
            # 判断尾景数据是否属于下月跨月数据（判断尾景数据起始日期与当月最后一日是否相等）
            if (day_month_list_last + 7) != days_this_month and month_index != 12:
                last_day_this_month_datetime = datetime.datetime.strptime(str(last_day_this_month), '%Y-%m-%d')
                delta_this_month_last = (last_day_this_month_datetime - date_month_list_last).days + 1
                month_list[-1][1] = delta_this_month_last / 8
            print(f'{month_index} month has {len(month_list)} rasters.')
            # LAI月尺度转换
            month_list_lai = []

            raster = RasterTiff()
            for lai_name_month in month_list:
                lai_rows, lai_columns, lai_bands, lai_geotrans, lai_proj, lai_data = raster.read_img(lai_name_month[0])
                lai_data = lai_data.astype(np.float32)
                # 列表参数顺序：影像名，权重，lai_rows, lai_columns, lai_bands, lai_geotrans, lai_proj, lai_data
                lai_name_month.extend([lai_rows, lai_columns, lai_bands, lai_geotrans, lai_proj, lai_data])
                month_list_lai.append(lai_name_month)
            # print(month_list_lai)
            # 根据权重进行月尺度转换
            lai_data_month_aggregation = np.zeros(shape=(month_list_lai[0][2], month_list_lai[0][3]), dtype=np.float32)

            for lai_data_month in month_list_lai:
                # 将异常值设为空值
                lai_data_month[-1][np.where((lai_data_month[-1] < 0) | (lai_data_month[-1] > 100))] = np.nan
                lai_data_month_aggregation = lai_data_month_aggregation + lai_data_month[1] * lai_data_month[-1]

            # 算出每个月的权重
            weight = 0
            for i in range(0, len(month_list)):
                weight = weight + month_list[i][1]
            print(f'The weight of {year_index}-{month_index} is {weight}.')
            # print()
            # pprint.pprint(month_list)
            Scale_Factor = 0.1
            lai_data_month_aggregation = lai_data_month_aggregation * Scale_Factor / weight
            raster.write_img(os.path.join(lai_8days_year_folder_path, f'LAI{year_index}_{month_index:02}.tif'), month_list_lai[0][5], month_list_lai[0][6], lai_data_month_aggregation)

print('done!')



