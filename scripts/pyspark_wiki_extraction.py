from pyspark.sql import SparkSession
from pyspark.sql import functions as F

import os

spark = (
    SparkSession.builder
    .appName("RemotePySpark")
    .master("spark://localhost:7077")
    .config("spark.driver.host", "host.docker.internal")
    .config("spark.driver.bindAddress", "0.0.0.0")
    .config("spark.driver.port", "7078")
    .config("spark.blockManager.port", "7079")
    .getOrCreate()
)

INPUT_FILES_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_input/enwiki-latest-pages-articles-multistream27.xml-p78975910p80475909.bz2"
INPUT_TEST_FILE_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_input/test_example/example.xml"

OUTPUT_FILES_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_output/"


xml_test =["""

    
    <page>
      <title>Page title</title>
      <restrictions>edit=sysop:move=sysop</restrictions>
      <revision>
        <timestamp>2001-01-15T13:15:00Z</timestamp>
        <contributor><username>Foobar</username></contributor>
        <comment>I have just one thing to say!</comment>
        <text>A bunch of text here.</text>
        <minor />
      </revision>
      <revision>
        <timestamp>2001-01-15T13:10:27Z</timestamp>
        <contributor><ip>10.0.0.2</ip></contributor>
        <comment>new!</comment>
        <text>An earlier revision.</text>
      </revision>
    </page>

"""]


REGEX_PATTERNS = {
    "INFOBOX":(
    r"(?m)^[ \t]*\|[ \t]*"
    r"([A-Za-z_][A-Za-z0-9_]*)"
    r"[ \t]*=[ \t]*(.*)$"
)
}

# One row per text file

df = spark.read.option("rowTag", "page").xml(INPUT_TEST_FILE_PATH)
new_df = df.select(F.col("revision")[0]["text"]["_VALUE"].cast("string").alias("text"))
new_df = new_df.select(
    F.regexp_extract_all("text", F.lit(REGEX_PATTERNS["INFOBOX"]), 0).alias("info_raw")
).select("info_raw", F.transform("info_raw", lambda info:F.split(F.regexp_replace(info, r"^\s*\|\s*", ""), r"\s*=\s*")).alias("info_table"))
new_df.printSchema()
new_df.select("info_table").show(truncate=False)
#df.select(F.regexp_extract_all("text", REGEX_PATTERNS["INFOBOX"]))

