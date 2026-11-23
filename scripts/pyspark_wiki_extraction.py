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

INPUT_FILES_PATH = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/spark_input/"
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
        r"(?s)\{\{.*?\}\}|\[\[|\]\]|<ref\b[^>]*>.*?</ref>|<ref\b[^>]*/>|<!--.*-->|'''|<.*>.+</.*>|\n"
    ),
    "WIKI_FILE":(
        r"(?is)\[\[(?:File|Image):(?:[^\[\]]|\[\[[^\[\]]*\]\])*\]\]"
    ),
    "FIRST_SECTION":(
        r"(?s)\}\}\s*\n\n(.*?\n\n)"
    ),
 "MIL_AIRCRAFT": (
    r"(?i)\b(?:"
    r"military|"
    r"fighter|"
    r"jet|"
    r"superiority|"
    r"multirole|"
    r"multi-role|"
    r"interceptor|"
    r"strike|"
    r"attack|"
    r"combat|"
    r"bomber|"
    r"strategic|"
    r"tactical|"
    r"reconnaissance|"
    r"surveillance|"
    r"warfare|"
    r"AWACS|"
    r"warplane|"
    r"warbird|"
    r"transport|"
    r"trainer|"
    r"carrier|"
    r"naval|"
    r"stealth|"
    r"supersonic|"
    r"airborne|"
    r"unmanned|"
    r"UCAV|"
    r"aircraft"
    r")\b"
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

df = spark.read.parquet(os.path.join(INPUT_FILES_PATH, "aircraft_articles/"))

# extract infobox, categories etc.
new_df = df.select("title", "text",
    F.regexp_extract("text", REGEX_PATTERNS["INFOBOX"], 1).alias("infobox"),
    F.regexp_extract("text", REGEX_PATTERNS["VARIANTS_SECTION"], 1).alias("variants_raw"),
    F.regexp_extract("text", REGEX_PATTERNS["CATEGORIES"],1).alias("categories"),
    F.regexp_extract("text", REGEX_PATTERNS["SPECS"], 1).alias("specs_box"),
    F.regexp_extract("text", REGEX_PATTERNS["FIRST_SECTION"], 1).alias("first_section")
)
# cleaning

new_df = new_df.select("title", "text", "categories",
    F.regexp_replace(F.regexp_replace("infobox", REGEX_PATTERNS["WIKI_FILE"], ""), REGEX_PATTERNS["CLEANING_GENERAL"], "").alias("infobox"),
    F.regexp_replace(F.regexp_replace("variants_raw", REGEX_PATTERNS["WIKI_FILE"], ""), REGEX_PATTERNS["CLEANING_GENERAL"], "").alias("variants_raw"),
    F.regexp_replace(F.regexp_replace("specs_box", REGEX_PATTERNS["WIKI_FILE"], ""), REGEX_PATTERNS["CLEANING_GENERAL"], "").alias("specs_box"),
    F.regexp_replace(F.regexp_replace("first_section", REGEX_PATTERNS["WIKI_FILE"], ""), REGEX_PATTERNS["CLEANING_GENERAL"], "").alias("first_section")
    

)

print("Before")
print(new_df.count())

new_df = new_df.filter(
    F.regexp_count(
        F.col("infobox"),
        F.lit(REGEX_PATTERNS["MIL_AIRCRAFT"])
    ) > 0
)

new_df = new_df.filter(
    F.regexp_count(F.col("infobox"), F.lit(r"\|")) > 0
)
print("After")

print(new_df.count())

# final extraction
new_df  = new_df.select("title", "categories", "first_section",
    F.map_from_arrays(
        F.regexp_extract_all("variants_raw", F.lit(REGEX_PATTERNS["VARIANT"]), 1),
        F.regexp_extract_all("variants_raw", F.lit(REGEX_PATTERNS["VARIANT"]), 2)
    ).alias("variants"),
    F.map_from_arrays(
        F.regexp_extract_all("infobox", F.lit(REGEX_PATTERNS["INFOBOX_FIELDS"]), 1),
        F.regexp_extract_all("infobox", F.lit(REGEX_PATTERNS["INFOBOX_FIELDS"]), 2)
    ).alias("info"),
    F.map_from_arrays(
            F.regexp_extract_all("specs_box", F.lit(REGEX_PATTERNS["INFOBOX_FIELDS"]), 1),
            F.regexp_extract_all("specs_box", F.lit(REGEX_PATTERNS["INFOBOX_FIELDS"]), 2)
    ).alias("specs")
)



spark.conf.set("spark.sql.caseSensitive", "true")
original_site_schema = StructType([ 
    StructField("title", StringType()),
    StructField("year", StringType()),
    StructField("country", StringType()),
    StructField("content_clear", StringType()),
    StructField("armament", StringType()),
    StructField("propulsion", StringType()),
    StructField("paramaters", StructType([
        StructField("Maximum Speed", StringType()),
        StructField("Service Ceiling", StringType()),
        StructField("Operational Range", StringType()),
        StructField("Rate-of-Climb", StringType()),
        StructField("Length", StringType()),
        StructField("Width", StringType()),
        StructField("Height", StringType()),
        StructField("Empty Weight", StringType()),
        StructField("MTOW", StringType()),
        StructField("Cruise Speed", StringType())
    ]))


])

def normalize_key(col):
    return F.regexp_replace(
        F.trim(F.regexp_replace(F.trim(F.lower(col)), r"\(.+?\)", "")), 
    r"\s+|/", "-")
    

original_site_df = spark.read.schema(original_site_schema).parquet(os.path.join(INPUT_FILES_PATH, "aircraft_articles_original_site/"))
original_site_df = original_site_df.drop_duplicates(["title"])

original_site_df = original_site_df.withColumn("title_key", normalize_key(F.col("title")))

original_site_df = original_site_df.filter(F.col("content_clear") != "")

METRIC_PARAMETER_FIELDS = {
    "maximum_speed_kph": ("Maximum Speed", r"^\s*([\d,]+(?:\.\d+)?)\s*kph\b"),
    "service_ceiling_m": ("Service Ceiling", r"^\s*([\d,]+(?:\.\d+)?)\s*m\b"),
    "operational_range_km": ("Operational Range", r"^\s*([\d,]+(?:\.\d+)?)\s*km\b"),
    "rate_of_climb_m_per_min": ("Rate-of-Climb", r"^\s*([\d,]+(?:\.\d+)?)\s*m\s*/\s*min\b"),
    "length_m": ("Length", r"^\s*([\d,]+(?:\.\d+)?)\s*m\b"),
    "width_m": ("Width", r"^\s*([\d,]+(?:\.\d+)?)\s*m\b"),
    "height_m": ("Height", r"^\s*([\d,]+(?:\.\d+)?)\s*m\b"),
    "empty_weight_kg": ("Empty Weight", r"^\s*([\d,]+(?:\.\d+)?)\s*kg\b"),
    "mtow_kg": ("MTOW", r"^\s*([\d,]+(?:\.\d+)?)\s*kg\b"),
}

for field_name, (parameter_name, metric_pattern) in METRIC_PARAMETER_FIELDS.items():
    metric_value = F.regexp_extract(
        F.col("paramaters").getField(parameter_name),
        metric_pattern,
        1
    )
    original_site_df = original_site_df.withColumn(
        field_name,
        F.regexp_replace(metric_value, ",", "").cast("double")
    )





new_df = new_df.withColumn("title_key", normalize_key(F.col("title")))

new_df.select("first_section").show(truncate=False, n=10)



merged_df_inner = (
    original_site_df.alias("original").
    join(new_df.alias("wiki"), original_site_df["title_key"] == new_df["title_key"], how="inner").select(
        F.col("original.title").alias("title"),
        F.col("original.year"),
        F.col("original.country"),
        F.col("original.content_clear"),
        F.col("original.armament"),
        F.col("original.propulsion"),
        F.col("original.paramaters"),
        *[F.col(f"original.{field_name}") for field_name in METRIC_PARAMETER_FIELDS],
        F.col("wiki.title").alias("wiki_title"),
        F.col("wiki.categories"),
        F.col("wiki.variants"),
        F.col("wiki.info"),
        F.col("wiki.specs"),
        F.col("original.title_key").alias("title_key")
    )
)

merged_df = (
    original_site_df.alias("original").
    join(new_df.alias("wiki"), original_site_df["title_key"] == new_df["title_key"], how="full_outer").select(
        F.col("original.title").alias("title"),
        F.col("original.year"),
        F.col("original.country"),
        F.coalesce(
            F.col("original.content_clear"),
            F.col("wiki.first_section")
        ),
        F.col("original.armament"),
        F.col("original.propulsion"),
        F.col("original.paramaters"),
        *[F.col(f"original.{field_name}") for field_name in METRIC_PARAMETER_FIELDS],
        F.col("wiki.title").alias("wiki_title"),
        F.col("wiki.categories"),
        F.col("wiki.variants"),
        F.col("wiki.info"),
        F.col("wiki.specs"),
  
        F.col("original.title_key").alias("title_key")
    )
)


'''
merged_df = (
    original_site_df.alias("original").
    join(new_df.alias("wiki"), original_site_df["title_key"] == new_df["title_key"], "inner")
)
'''
'''
merged_df = merged_df.withColumn("ratio", F.levenshtein("original.title_key", "wiki.title_key"))
merged_df.select("wiki.title_key", "original.title_key", "ratio").show(1300, truncate=False)

'''





print(original_site_df.count())
print(merged_df.count())
print(merged_df_inner.count())


merged_df_inner.printSchema()

merged_df_inner.select(*METRIC_PARAMETER_FIELDS.keys()).show(truncate=True, n=10)

merged_df.write.mode("overwrite").json(
    OUTPUT_FILES_PATH + "aircraft_articles_after_join"
)



