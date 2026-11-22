## Run lucene
 
```

Run using
docker run --rm -it \
  -v "$(pwd)/data/input:/input" \
  -v "$(pwd)/data/output:/output" \
  lucene

docker build -t lucene . && \
docker run --rm -it \
  -v "$(pwd)/data/input:/input" \
  -v "$(pwd)/data/output:/output" \
  lucene

  python pylucene.py index
  python run_pylucene_tests.py
```