import numpy as np
import pandas as pd
import os

from pyclustering.cluster.kmeans import *
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer

from multiprocessing import Pool

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def import_sdss (sdss_filepath: str) -> pd.DataFrame:
    sdss_colwidths = [6, 6, 2, 5, 6, 9, 9, 15, 11, 11, 11, 11, 12, 9, 7, 8, 7,
                        8, 8, 7, 5, 6, 5, 6, 5, 6, 5, 6, 5, 6, 5, 7, 6, 2, 8, 21,
                        3, 3, 12, 11,  6, 9, 8, 6, 20, 8, 5, 6, 14, 13, 11, 11,
                        11, 11, 11, 21, 14, 11, 11]
    sdss_datatypes = {"SMOC_ID": str, "OBJ_ID_RUN": np.int32,
                    "OBJ_ID_COL": np.int32, "OBJ_ID_FIELD": np.int32,
                    "OBJ_ID_OBJ": np.int32, "ROWC": np.float32,
                    "COLC": np.float32, "JD_ZERO": np.float32,
                    "RA": np.float32, "DEC": np.float32,
                    "LAMBDA": np.float32, "BETA": np.float32,
                    "PHI": np.float32, "VMU": np.float32,
                    "VMU_ERROR": np.float32, "VNU": np.float32,
                    "VNU_ERROR": np.float32, "VLAMBDA": np.float32,
                    "VBETA": np.float32, "U_MAG": np.float64,
                    "U_ERR": np.float64, "G_MAG": np.float64,
                    "G_ERR": np.float64, "R_MAG": np.float64,
                    "R_ERR": np.float64, "I_MAG": np.float64,
                    "I_ERR": np.float64, "Z_MAG": np.float64,
                    "Z_ERR": np.float64, "A_MAG": np.float32,
                    "A_ERR": np.float32, "V_MAG": np.float32,
                    "B_MAG": np.float32, "IDFLAG": np.int32,
                    "AST_NUMBER": np.int32, "PROV_ID": str,
                    "D_COUNTER": np.int32, "TOTAL_D_COUNT": np.int32,
                    "RA_COMPUTED": np.float32, "DEC_COMPUTED": np.float32,
                    "V_MAG_COMPUTED": np.float32, "R_DIST": np.float32,
                    "G_DIST": np.float32, "PHASE": np.float32,
                    "OSC_CAT_ID":str, "H": np.float32,
                    "G": np.float32, "ARC": np.int32,
                    "EPOCH_OSC": np.float32,
                    "A_OSC": np.float32, "E_OSC": np.float32,
                    "I_OSC": np.float32, "LON_OSC": np.float32,
                    "AP_OSC": np.float32, "M_OSC": np.float32,
                    "PROP_CAT_ID": str, "A_PROP": np.float32,
                    "E_PROP": np.float32, "SIN_I_PROP": np.float32}

    return pd.read_fwf(sdss_filepath, widths=sdss_colwidths, sep='\t',
                       header=None, names=list(sdss_datatypes.keys()),
                       dtype=sdss_datatypes)

def import_tax (tax_filepath: str) -> pd.DataFrame:
    tax_datatypes = {'AST_NUMBER': np.int32, 'AST_NAME': str,
                     'PROV_ID': str, 'CLASSIFICATION': str,
                     'SCORE': np.int32, 'NCLASS': np.int32,
                     'METHOD': np.int32, 'BAD': np.int32,
                     'SEQUENCE': str, 'MOID': str,
                     'H': np.float32, 'PROPER_SEMIMAJOR_AXIS': np.float32,
                     'PROPER_ECCENTRICITY': np.float32,
                    'SINE_OF_PROPER_INCLINATION': np.float32,
                    'OSC_SEMIMAJOR_AXIS': np.float32,
                    'OSC_ECCENTRICITY': np.float32,
                    'OSC_INCLINATION': np.float32}
    taxfwflist = [6, 18, 12, 3, 3, 2, 2, 3, 10, 6, 7, 7, 7, 7, 8, 7, 9]
    return pd.read_fwf(tax_filepath, widths=taxfwflist, sep='\t',
                       header=None, names=list(tax_datatypes.keys()),
                       dtype=tax_datatypes)


def plot_5d(feature_x, feature_y, feature_z, feature_color, feature_size,
            x_label, y_label, z_label, c_label, s_label, title,
            fig_size=(14, 10)):
    fig = plt.figure(figsize=fig_size)
    fig.suptitle(title, fontsize=14)
    ax = fig.add_subplot(111, projection='3d')

    normalization = max(feature_color)
    actual_colors = [(0, c_val / normalization, c_val / normalization)
                     for c_val in feature_color]
    ax.scatter(feature_x, feature_y, feature_z, alpha=0.4,
           c=actual_colors, edgecolors='none', s=feature_size)
    
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)

def draw_5d_clusters(feature_x, feature_y, feature_z, feature_color,
                     feature_size, clusters, x_label, y_label, z_label,
                     c_label, s_label, title, fig_size=(14, 10)):
    
    fig = plt.figure(figsize=fig_size)
    fig.suptitle(title, fontsize=14)
    ax = fig.add_subplot(111, projection='3d')

    for i, cluster in enumerate(clusters):
        normalization = max(feature_color.loc[cluster])
        actual_colors = [(i/len(clusters), c_val / normalization, c_val / normalization)
                            for c_val in feature_color.loc[cluster]]
        ax.scatter(feature_x.loc[cluster], feature_y.loc[cluster],
                    feature_z.loc[cluster], alpha=0.4, c=actual_colors,
                    edgecolors='none', s=feature_size.loc[cluster])
    
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)

def calc_ref_colors(df, columns, refl_list):
    for i in range(0, len(columns) - 1):
        df[columns[i] + "_REFL_COLOR"] = df[columns[i]] - df[columns[i + 1]] - refl_list[i]

#def calc_reflect_color_grad(df, columns, reference_list):
#    for i in range(1, len(columns))
#        df[column + "_GRAD"] = ()

def k_means_pp(data, num_clusters):
    centers = kmeans_plusplus_initializer(data, num_clusters).initialize()

    # create instance of K-Means algorithm
    kmeans_instance = kmeans(data, centers)

    # run cluster analysis and obtain results
    kmeans_instance.process();
    centers = kmeans_instance.get_clusters();
    error = kmeans_instance.get_total_wce()

    return (centers, error)

def apply_classification(df, cluster_list, classification_col_name):
    for i in range(len(cluster_list)):
        df.loc[cluster_list[i], classification_col_name] = i

def merge(df1, df2, on):
    merged = pd.merge(df1, df2, sort=False, on=on, how='outer', indicator=False)
    return merged.dropna()

def compare_results(df, classification_col_name, other_class_col):
    all_ratios = []

    for class_type in df[classification_col_name].unique():
        subset_df = df.loc[df[classification_col_name] == class_type]
        count_dict = {}
        
        for value in subset_df[other_class_col]:
            if value in count_dict:
                count_dict[value] += 1
            else:
                count_dict[value] = 1
        all_ratios.append((class_type, count_dict))
    
    return all_ratios
