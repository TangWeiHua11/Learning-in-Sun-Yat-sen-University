import os
import arcpy

filepath = r'E:\DATA\ET\fET\Raster'
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')

files = os.listdir(filepath)

for filename in files:
    if filename.endswith('.tif') and 2004 <= int(filename[3:7]) <= 2016:
        in_raster = os.path.join(filepath, filename)
        rectangle = ''
        out_raster = os.path.join(filepath, 'Clip', filename)
        in_template_dataset = r'D:\论文\我的论文\河流水化学组成的时空变化特征及其影响因素的研究\data\最新2021年全国行政区划\省.shp'
        nodata_value = ''
        clipping_geometry = 'ClippingGeometry'
        maintain_clipping_extent = 'NO_MAINTAIN_EXTENT'
        arcpy.management.Clip(in_raster, rectangle, out_raster, in_template_dataset,
                              nodata_value, clipping_geometry, maintain_clipping_extent)
        print(f'{filename}裁剪成功。')
print('done!')
