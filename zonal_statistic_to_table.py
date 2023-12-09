import os
import arcpy
from arcpy.sa import *

path = r'E:\NPP'
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'D:\我的论文\中国河流水化学组成的时空变化特征及其影响因素的研究\河流水化学组成的时空变化特征及其影响因素的研究\data\流域NPP.gdb'

in_zone_data = r'D:\我的论文\中国河流水化学组成的时空变化特征及其影响因素的研究\河流水化学组成的时空变化特征及其影响因素的研究\data\地图.gdb\流域_连接'
zone_field = '代码'
China_map = r'D:\我的论文\中国河流水化学组成的时空变化特征及其影响因素的研究\河流水化学组成的时空变化特征及其影响因素的研究\data\地图.gdb\省_融合'
for year_index in range(2004, 2017):
    sub_path = os.path.join(path, str(year_index))
    for tif_file in os.listdir(sub_path):
        if len(tif_file) < 15:
            # 裁剪
            in_raster = os.path.join(sub_path, tif_file)
            rectangle = ''
            if os.path.exists(os.path.join(sub_path, 'China')):
                pass
            else:
                os.mkdir(os.path.join(sub_path, 'China'))
            if os.path.exists(os.path.join(sub_path, 'China', tif_file)):
                print(f'The file {tif_file} is existed.')
                continue
            else:
                out_clip_raster = os.path.join(sub_path, 'China', tif_file)
                in_template_dateset = China_map
                nodata_value = ''
                clipping_geometry = True
                maintain_clipping_extent = 'NO_MAINTAIN_EXTENT'
                arcpy.management.Clip(in_raster, rectangle, out_clip_raster, in_template_dateset, nodata_value, clipping_geometry, maintain_clipping_extent)
                print(f'Clipping {tif_file} successfully.')

            # 投影栅格
            in_project_raster = out_clip_raster
            if os.path.exists(os.path.join(sub_path, 'China', 'Projection')):
                pass
            else:
                os.mkdir(os.path.join(sub_path, 'China', 'Projection'))

            out_project_raster = os.path.join(sub_path, 'China', 'Projection', tif_file)
            out_coor_system = arcpy.SpatialReference('WGS 1984 UTM Zone 50N')
            resampling_type = 'NEAREST'
            cell_size = 150
            arcpy.management.ProjectRaster(in_project_raster, out_project_raster, out_coor_system, resampling_type, cell_size)
            print(f'Projecting {tif_file} is successfully.')

            # 分区统计
            in_value_raster = out_project_raster
            out_table = tif_file[: -4]
            ignore_nodata = True
            statistics_type = 'MEAN'
            outZSaT = ZonalStatisticsAsTable(in_zone_data, zone_field, in_value_raster, out_table, ignore_nodata, statistics_type)
            print(f'Statistics {tif_file} is finished!')
print('done!')