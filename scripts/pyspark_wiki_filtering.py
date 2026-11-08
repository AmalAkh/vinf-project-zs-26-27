from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
)
import os
from pathlib import Path

spark = (
    SparkSession.builder
    .appName("MyPySparkJob")
    .master("local[8]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.sql.shuffle.partitions", "16")
    .getOrCreate()
)

INPUT_FILES_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_input/enwiki-latest-pages-articles.xml.bz2"
INPUT_TEST_FILE_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_input/test_example/example.xml"

OUTPUT_FILES_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_output/"



REGEX_PATTERNS = {
    "INFOBOX":(
    r"(?m)^[ \t]*\|[ \t]*"
    r"([A-Za-z_][A-Za-z0-9_]*)"
    r"[ \t]*=[ \t]*(.*)$"
    ),
    "VARIANTS_SECTION": (
        r"(?ms)^[ \t]*==[ \t]*Variants[ \t]*==[ \t]*\r?\n"
        r"(.*?)"
        r"(?=^[ \t]*==(?!=)[^\r\n]*==[ \t]*\r?$|\z)"
    ),
    "VARIANT":(
        r"(?m)[ \t]*;[ \t]*([^:\r\n]+):[ \t]*(.*?)(?=,\s*;|$)"
    ),
    "AIRCRAFT":(
        r"(?i)\[\[\s*category\s*:"
        r"[^\]\|\n]*?"
        r"(aircraft|airplane|glider|helicopter)"
        r"[^\]\|\n]*?"
        r"\]\]"
    ),
    "INFOBOX_AIRCRAFT":(
        r"(?i)\{\{\s*infobox[\s_]+(aircraft|helicopter)\r?\n"
    )
}

schema = StructType([
    StructField("title", StringType()),
    StructField("ns", LongType()),
    StructField("id", LongType()),
    StructField("revision", StructType([
        StructField("text", StringType())
    ]))
])

sc = spark.sparkContext

rdd = sc.newAPIHadoopFile(INPUT_FILES_PATH, 
    inputFormatClass=(
        "org.apache.spark.sql.execution.datasources.xml.XmlInputFormat"
    ),
    keyClass="org.apache.hadoop.io.LongWritable",
    valueClass="org.apache.hadoop.io.Text",
    conf={
        "xmlinput.start": "<page>",
        "xmlinput.end": "</page>",
        "mapreduce.input.fileinputformat.split.minsize":
            str(256 * 1024 * 1024),
    }
).values()
print("Input partitions:", rdd.getNumPartitions())
df = spark.createDataFrame(
    rdd.map(lambda xml: (xml,)),
    schema="raw_xml STRING"
)
df = df.select(F.from_xml("raw_xml", schema).alias("page")).select("page.*")
df.printSchema()
#new_df = df.select("title",F.col("revision")["text"].cast("string").alias("text"))
print("Available Spark parallelism:",
      spark.sparkContext.defaultParallelism)

print("Input files:", len(df.inputFiles()))
print("Default partitions:", df.rdd.getNumPartitions())

only_articles_df = (
    df.filter(F.col("ns") == 0)
    .select(
        F.col("id").alias("page_id"),
        F.col("title"),
        F.col("revision.text").alias("text")
    )
)
only_articles_df = only_articles_df.filter(F.regexp_like("text", F.lit(REGEX_PATTERNS["INFOBOX_AIRCRAFT"])))

# This DOES trigger actual reading of the dump.
only_articles_df.show(50, truncate=80)
only_articles_df.write.mode("overwrite").parquet(
    OUTPUT_FILES_PATH + "aircraft_articles"
)
print(only_articles_df.count())



'''
# One row per text file

df = spark.read.option("rowTag", "page").xml(INPUT_FILES_PATH)
new_df = df.select("title",F.col("revision")["text"].cast("string").alias("text"))


# clear text from special wiki markup symbols
new_df = new_df.select("title", F.regexp_replace("text", r"(?s)\{\{.*?\}\}|\[\[|\]\]|<ref\b[^>]*>.*?</ref>|<ref\b[^>]*/>|<!--.*-->", "").alias("text_clear"))

# Extract information from the info table
new_df = new_df.select("title", "text_clear",                     
    F.regexp_extract_all("text_clear", F.lit(REGEX_PATTERNS["INFOBOX"]), 0).alias("info_raw")
).select("title", "text_clear", F.transform("info_raw", lambda info:F.split(F.regexp_replace(info, r"^\s*\|\s*", ""), r"\s*=\s*")).alias("info_table"))

new_df = new_df.select("title", "text_clear", "info_table" ,
    F.regexp_extract("text_clear", REGEX_PATTERNS["VARIANTS_SECTION"], 1).alias("variants_raw"))


new_df = new_df.select("title", "info_table", "text_clear", "variants_raw",
    F.map_from_arrays(
        F.regexp_extract_all("variants_raw", F.lit(REGEX_PATTERNS["VARIANT"]), 1),
        F.regexp_extract_all("variants_raw", F.lit(REGEX_PATTERNS["VARIANT"]), 2)
    ).alias("variants")
)

new_df.printSchema()
new_df.select("info_table").show(truncate=False)
new_df.write.mode("overwrite").json(os.path.join(OUTPUT_FILES_PATH,"wiki_data.json"))
#df.select(F.regexp_extract_all("text", REGEX_PATTERNS["INFOBOX"]))

'''