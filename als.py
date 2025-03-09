import pyspark
from pyspark.ml.recommendation import ALS
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import StringType, FloatType, IntegerType, LongType

from recommenders.utils.timer import Timer
from recommenders.datasets import movielens
from recommenders.utils.notebook_utils import is_jupyter
from recommenders.datasets.spark_splitters import spark_random_split
from recommenders.evaluation.spark_evaluation import SparkRatingEvaluation, SparkRankingEvaluation
from recommenders.utils.spark_utils import start_or_get_spark
from recommenders.utils.notebook_utils import store_metadata

COL_USER = 'UserID'
COL_ITEM = 'FundID'
COL_RATING = 'Star'


def is_user_rated(data, userID):
    return userID in data[COL_USER].unique()

def convert_to_spark_df(data, schema):
    return pyspark.sql.SparkSession.builder.getOrCreate().createDataFrame(data, schema)


def train(data):
    header = {
    "userCol": COL_USER,
    "itemCol": COL_ITEM,
    "ratingCol": COL_RATING,
}
    als = ALS(
        rank=10,
        maxIter=15,
        implicitPrefs=False,
        regParam=0.05,
        coldStartStrategy='drop',
        nonnegative=False,
        seed=42,
        **header
    )


if __name__ == "__main__":
    pass