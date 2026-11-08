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
    .config("spark.sql.mapKeyDedupPolicy", "LAST_WIN")
    .getOrCreate()
)

INPUT_FILES_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_input/aircraft_articles/"
INPUT_TEST_FILE_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_input/test_example/example.xml"

OUTPUT_FILES_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_output/"



REGEX_PATTERNS = {
    "INFOBOX_FIELDS":(
    r"(?m)^[ \t]*\|[ \t]*"
    r"([A-Za-z_][A-Za-z0-9_]*)"
    r"[ \t]*=[ \t]*(.*)$"
    ),
    "INFOBOX":(
        r"(?s)\{\{Infobox aircraft(.*?)\}\}"
    ),

    "SPECS":(
        r"(?s)\{\{Aircraft specs(.*?)\}\}"
    ),
    
    "VARIANTS_SECTION": (
        r"(?ms)^[ \t]*==[ \t]*Variants[ \t]*==[ \t]*\r?\n"
        r"(.*?)"
        r"(?=^[ \t]*==(?!=)[^\r\n]*==[ \t]*\r?$|\z)"
    ),
    "VARIANT":(
        r"(?m)(?:'*)?[ \t]*;?[ \t]*(?:'*)([^'\n\r:]+)(?:'{2,3})?\n?\r?:[ \t]*(.*?)(?=,\s*;|$)"
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
    ),
    "CATEGORIES":(
        r"(?s)\[\[Category:(.*?)\]\]"
    ),
    "CLEANING_GENERAL":(
        r"(?s)\{\{.*?\}\}|\[\[|\]\]|<ref\b[^>]*>.*?</ref>|<ref\b[^>]*/>|<!--.*-->|'''|<.*>.+</.*>"
    ),
    "WIKI_FILE":(
        r"(?is)\[\[(?:File|Image):(?:[^\[\]]|\[\[[^\[\]]*\]\])*\]\]"
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

# One row per text file

df = spark.read.parquet(INPUT_FILES_PATH)

# extract infobox, categories etc.
new_df = df.select("title", "text",
    F.regexp_extract("text", REGEX_PATTERNS["INFOBOX"], 1).alias("infobox"),
    F.regexp_extract("text", REGEX_PATTERNS["VARIANTS_SECTION"], 1).alias("variants_raw"),
    F.regexp_extract("text", REGEX_PATTERNS["CATEGORIES"],1).alias("categories"),
    F.regexp_extract("text", REGEX_PATTERNS["SPECS"], 1).alias("specs_box")
)
# cleaning

new_df = new_df.select("title", "text", "categories",
    F.regexp_replace(F.regexp_replace("infobox", REGEX_PATTERNS["WIKI_FILE"], ""), REGEX_PATTERNS["CLEANING_GENERAL"], "").alias("infobox"),
    F.regexp_replace(F.regexp_replace("variants_raw", REGEX_PATTERNS["WIKI_FILE"], ""), REGEX_PATTERNS["CLEANING_GENERAL"], "").alias("variants_raw"),
    F.regexp_replace(F.regexp_replace("specs_box", REGEX_PATTERNS["WIKI_FILE"], ""), REGEX_PATTERNS["CLEANING_GENERAL"], "").alias("specs_box")


)
# final extraction
new_df  = new_df.select("title", "text", "categories",
    F.map_from_arrays(
        F.regexp_extract_all("variants_raw", F.lit(REGEX_PATTERNS["VARIANT"]), 1),
        F.regexp_extract_all("variants_raw", F.lit(REGEX_PATTERNS["VARIANT"]), 2)
    ).alias("variants"),
    F.map_from_arrays(
        F.regexp_extract_all("infobox", F.lit(REGEX_PATTERNS["INFOBOX_FIELDS"]), 1),
        F.regexp_extract_all("infobox", F.lit(REGEX_PATTERNS["INFOBOX_FIELDS"]), 2)
    ).alias("info")
)
print(new_df.rdd.getNumPartitions())
new_df.printSchema()
new_df.show(100, truncate=True)
print(new_df.count())