"""utils scripts for preprocessing data by using method of the class FeatureTools"""

import json
import pickle
import logging
import pandas as pd
import warnings
from pathlib import Path
from utils.feature_tools import FeatureTools

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                    datefmt='%d/%m/%Y %H:%M ',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

from pyspark.sql.session import SparkSession
import pyspark.sql.types as tp
from pyspark.ml import Pipeline
from pyspark.ml.feature import StandardScaler
from pyspark.sql import Row, Column
from pyspark.sql.functions import udf

warnings.filterwarnings("ignore")
###################################################
# Spark Configuration
###################################################

spark = SparkSession\
    .builder\
    .appName('FraudTransaction')\
    .master('local')\
    .getOrCreate()

# define the schema
my_schema = tp.StructType([
    tp.StructField(name='Time', dataType= tp.FloatType(),  nullable= True),
    tp.StructField(name='V1', dataType= tp.FloatType(),  nullable= True),
    tp.StructField(name='V2', dataType= tp.FloatType(),   nullable= True)
    ])


def load_new_training_data(path):
    data = []
    with open(path, "r") as f:
        for line in f:
            data.append(json.loads(line))
        df = pd.DataFrame(data)  # so that hasattr(df, columns)
    return spark.createDataFrame(df)

def build_train(train_path, result_path, dataprocessor_id=0, PATH_2=None):

    target ='Class'
    #read initial DataFrame
    #df = spark.read.csv(train_path, header=True, schema=my_schema)
    df = spark.read.csv(train_path, header=True)

    if PATH_2:
        df_tmp = load_new_training_data(PATH_2)
        #in order to be consistent with df
        df_tmp = df_tmp[df.columns]
        # concatenate for a new DataFrame
        df = df.union(df_tmp)
        #ALERT: save on Disk, this operation could be dangerous for Big Amount of Data
        df.write.csv(train_path)

    # UDF for converting clumns type from vector to double type
    unlist = udf(lambda x: round(float(list(x)[0]), 3), tp.DoubleType())
    preprocessor = FeatureTools()
    logger.info(f'Preprocessing Data: {df.columns}')
    for column in df.columns:
        df = df.withColumn(column, unlist(column))
        dataprocessor = preprocessor.fit(
                df,
                target,
                df.columns,
                StandardScaler(inputCol=column, outputCol=column+'_scd')
            )

    dataprocessor_fname = f'dataprocessor_{dataprocessor_id}.p'
    pickle.dump(dataprocessor, open(result_path/dataprocessor_fname, "wb"))
    if dataprocessor_id == 0:
        logger.info(f'Save column_order.p in: {result_path}')
        pickle.dump(df.columns[:-1], open(result_path / 'column_order.p', "wb"))

    return dataprocessor





