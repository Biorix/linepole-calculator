# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import osgeo.gdal as gdal
import affine
from geopy import distance
from .Mesures import lonlat_to_xy


class PixelInRange:
    def __init__(self, tif_path, lines, buffer_dist=1000, line_names=None):
        self.tif_ds = gdal.Open(tif_path)

        if line_names is None:
            line_names = np.arange(lines.shape[0])

        lat_start = lines[:, 0]
        lon_start = lines[:, 1]
        lat_end = lines[:, 2]
        lon_end = lines[:, 3]

        min_l_lat = np.amin(lines[:, [0, 2]])
        max_l_lat = np.amax(lines[:, [0, 2]])
        min_l_lon = np.amin(lines[:, [1, 3]])
        max_l_lon = np.amax(lines[:, [1, 3]])

        dx_min_lat = distance.distance((min_l_lat, min_l_lon), (min_l_lat, max_l_lon)).m
        dx_max_lat = distance.distance((max_l_lat, min_l_lon), (max_l_lat, max_l_lon)).m
        dx = (dx_max_lat + dx_min_lat) / 2
        dy = distance.distance((min_l_lat, min_l_lon), (max_l_lat, min_l_lon)).m

        min_lon = min_l_lon - (max_l_lon - min_l_lon) / dx * buffer_dist
        max_lon = max_l_lon + (max_l_lon - min_l_lon) / dx * buffer_dist
        min_lat = min_l_lat - (max_l_lat - min_l_lat) / dy * buffer_dist
        max_lat = max_l_lat + (max_l_lat - min_l_lat) / dy * buffer_dist

        dx_min_lat = distance.distance((min_lat, min_lon), (min_lat, max_lon)).m
        dx_max_lat = distance.distance((max_lat, min_lon), (max_lat, max_lon)).m
        dy = distance.distance((min_lat, min_lon), (max_lat, min_lon)).m

        forward_transform = affine.Affine.from_gdal(*self.tif_ds.GetGeoTransform())
        reverse_transform = ~forward_transform
        px_min, py_min = reverse_transform * (min_lon, min_lat)
        px_max, py_max = reverse_transform * (max_lon, max_lat)
        px_min, py_min = int(px_min), int(py_min)
        px_max, py_max = int(px_max), int(py_max)

        d_px = px_max - px_min + 1
        d_py = py_min - py_max + 1

        tif_arr = np.array(self.tif_ds.GetRasterBand(1).ReadAsArray(px_min, py_max, d_px, d_py))

        px_width = (max_lon - min_lon) / d_px
        py_height = (max_lat - min_lat) / d_py

        lon_px = np.arange(min_lon + px_width/2, max_lon, px_width)
        lon_px = np.tile(lon_px, (d_py, 1))
        lat_py = np.arange(max_lat - py_height/2, min_lat, -py_height)

        lat_py = np.tile(lat_py, (d_px, 1))
        lat_py = np.transpose(lat_py)

        x_px, y_py = lonlat_to_xy(dx_min_lat=dx_min_lat, dx_max_lat=dx_max_lat, dy=dy, min_lon=min_lon,
                                            max_lon=max_lon, min_lat=min_lat, max_lat=max_lat, lon = lon_px,
                                            lat = lat_py)

        x_start, y_start = lonlat_to_xy(dx_min_lat=dx_min_lat, dx_max_lat=dx_max_lat, dy=dy, min_lon=min_lon,
                                            max_lon=max_lon, min_lat=min_lat, max_lat=max_lat, lon = lon_start,
                                            lat = lat_start)

        x_end, y_end = lonlat_to_xy(dx_min_lat=dx_min_lat, dx_max_lat=dx_max_lat, dy=dy, min_lon=min_lon,
                                            max_lon=max_lon, min_lat=min_lat, max_lat=max_lat, lon = lon_end,
                                            lat = lat_end)


        tif_arr = np.dstack((tif_arr, x_px))
        tif_arr = np.dstack((tif_arr, y_py))

        flat_tif_arr = np.reshape(tif_arr, (d_px * d_py, 3))
        self.flat_tif_arr = flat_tif_arr[~np.isnan(flat_tif_arr).any(axis=1)]


        l_columns = ['x_start', 'y_start', 'x_end', 'y_end', 'pixel_sum']
        l_coord = np.concatenate((x_start[:, None], y_start[:, None], x_end[:, None], y_end[:, None]), axis=1)

        self.line_df = pd.DataFrame(index=line_names, columns=l_columns)
        self.line_df[l_columns[:-1]] = l_coord

    def eval_pixel_in_range(self, dist=600):
        tif = self.flat_tif_arr

        for i, row in self.line_df.iterrows():

            x_s = self.line_df['x_start'][i]
            y_s = self.line_df['y_start'][i]
            x_e = self.line_df['x_end'][i]
            y_e = self.line_df['y_end'][i]

            x_sp = x_s - tif[:, 1]
            x_ep = x_e - tif[:, 1]
            y_sp = y_s - tif[:, 2]
            y_ep = y_e - tif[:, 2]

            l_se = ((x_s-x_e)**2 + (y_s-y_e)**2)**0.5
            l_sp = (x_sp ** 2 + y_sp ** 2) ** 0.5
            l_ep = (x_ep ** 2 + y_ep ** 2) ** 0.5
            d = np.absolute((x_e-x_s)*y_sp-x_sp*(y_e-y_s))/l_se
            l_max = np.maximum(l_sp, l_ep)
            l_min = np.minimum(l_sp, l_ep)
            in_segment = (l_max ** 2 - d ** 2) < (l_se ** 2)
            in_segment_range = d < dist
            in_end_range = l_min < dist

            in_range = np.logical_or(np.logical_and(in_segment, in_segment_range), in_end_range)
            not_in_range = np.invert(in_range)
            tif_in_range = tif[in_range]

            print(d[in_range])

            self.line_df['pixel_sum'][i] = np.sum(tif_in_range[: ,0])

            tif = tif[not_in_range]


    def line_df_to_csv(self, path='lines.csv'):
        self.line_df.to_csv(path)
