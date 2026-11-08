from pyspark.sql import SparkSession
from pyspark.sql import functions as F


REGEX_PATTERNS = {
    "title_main": (
        r'<h1[^>]*class="[^">]*"[^>]*>'
        r'<span[^">]*class="[^">]*"[^">]*>(.+)</span></h1>'
    ),

    "title_fallback": r'<title[^>]*>(.+?)</title>',

    "description": (
        r'<!--BODYTEXT\d+-->\s*'
        r'<div[^>]*class="[^"]*contentStripOuter[^>]*"[^"]*>.*?'
        r'<span[^>]*class="[^"]*"[^>]*>\s*(.*?)\s*</span>.*?'
        r'<!--BODYTEXT\d+-->\s*'
    ),

    "description_html_cleanup": r'</?[^>]+\s*/?>',

    "description_whitespace_cleanup": r'\s{2,}',

    "variants": (
        r'<button[^>]*class="[^"]*collapsible[^"]*picTrans[^"]*"[^>]*>.*?Variants.*?</button>\s*'
        r'<div[^>]*class="[^"]*dropdownContent[^"]*"[^>]*>\s*'
        r'<div[^>]*>\s*'
        r'<span[^>]*class="[^"]*textDkGray[^"]*textNormal"[^>]*>(.*?)</span>'
    ),

    "performance_parameters": (
        r'<div[^>]*class="specContainerMain[^"]*">\s*'
        r'<span[^>]*class="[^">]*textNormal[^">]*">([^<]+)</span>\s*'
        r'<br\s*/?>\s*'
        r'<span[^>]*class="[^">]*textBold[^">]*">[^<]+</span>\s*'
        r'<br\s*/?>\s*'
        r'<span[^>]*class="[^">]*textNormal[^">]*">\(([^<]+)\)</span>\s*'
        r'</div>'
    ),

    "unit_produced": r'Total Production:.+ (\d+?) Units',

    "operators": (
        r'<a\s[^>]*'
        r'class="picTrans"[^>]*'
        r'title="[^"]*nation of (?:the )?([^"]+)"'
        r'[^>]*>'
    ),

    "roles": (
        r'<div[^>"]+class="roleContainers[^>"]*">([^>]+)'
        r'</div>'
    ),

    "country_and_year": (
        r'<h3[^>]*class="[^"]*">\s*([^|>]+?)\s*\|\s*([^|>]+?)</h3>'
    ),

    "armament": (
        r'<button[^>]*class="[^"]*collapsible[^"]*picTrans[^"]*"[^>]*>.*?Armament.*?</button>\s*'
        r'<div[^>]*class="[^"]*dropdownContent[^"]*"[^>]*>\s*'
        r'<div[^>]*>\s*'
        r'<span[^>]*class="[^"]*textDkGray[^"]*textNormal"[^>]*>(.*?)</span>'
    ),

    "propulsion": (
        r'<div[^>]*class="[^"]*specContainerMain[^"]*">\s*'
        r'<span[^>]*class="[^">]*">.*?Propulsion.*?</span>\s*'
        r'<br\s*/?>\s*'
        r'<span[^>]*class="[^">]*">\s*([^>]*)\s*</span>'
    ),

    "html_tag_cleanup": r'</?[^>]+>',

    "links_primary": (
        r'<(a|div)\b[^>]*\s(?:href|data-url)="([^"]*)"[^>]*>([^<]*)</\1>'
    ),

    "links_secondary": (
        r'<(a|div)\b[^>]*\s(?:href|data-url)="([^"]*)"\s'
        r'[^>]*title="([^>"]+)"\s*[^>]*>[\s\S]*?</\1>'
    ),
}
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

INPUT_FILES_FOLDER = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/raw_data/"
OUTPUT_FOLDER = "/Users/amalakhmadinurov/Desktop/ZS_2026_2027/VINF/Project/data/output/"


# One row per text file
df = spark.read.text(
    INPUT_FILES_FOLDER,
    wholetext=True
)

new_df = df.select(
    # Titles
    F.regexp_extract(
        "value", REGEX_PATTERNS["title_main"], 1
    ).alias("title_main"),

    F.regexp_extract(
        "value", REGEX_PATTERNS["title_fallback"], 1
    ).alias("title_fallback"),

    # Description
    F.regexp_extract(
        F.col("value"), F.lit("(?s)" + REGEX_PATTERNS["description"]), 1
    ).alias("description"),

    # Variants
    F.regexp_extract_all(
        "value", F.lit(REGEX_PATTERNS["variants"]), 1
    ).alias("variants"),

    # Performance parameters (two capture groups)
    F.regexp_extract_all(
        "value", F.lit(REGEX_PATTERNS["performance_parameters"]), 1
    ).alias("performance_parameter_names"),

    F.regexp_extract_all(
        "value", F.lit(REGEX_PATTERNS["performance_parameters"]), 2
    ).alias("performance_parameter_values"),

    # Production
    F.regexp_extract(
        "value", REGEX_PATTERNS["unit_produced"], 1
    ).alias("unit_produced"),

    # Operators
    F.regexp_extract_all(
        "value", F.lit(REGEX_PATTERNS["operators"]), 1
    ).alias("operators"),

    # Roles
    F.regexp_extract_all(
        "value", F.lit(REGEX_PATTERNS["roles"]), 1
    ).alias("roles"),

    # Country and year (two capture groups)
    F.regexp_extract(
        "value", REGEX_PATTERNS["country_and_year"], 1
    ).alias("country"),

    F.regexp_extract(
        "value", REGEX_PATTERNS["country_and_year"], 2
    ).alias("year"),

    # Armament
    F.regexp_extract_all(
        "value", F.lit(REGEX_PATTERNS["armament"]), 1
    ).alias("armament"),

    # Propulsion
    F.regexp_extract_all(
        "value", F.lit(REGEX_PATTERNS["propulsion"]), 1
    ).alias("propulsion"),

   
)
print(new_df.collect()[-1244])
new_df.write \
    .mode("overwrite") \
    .json(OUTPUT_FOLDER + "ships.json")
