"""Basic Oris runtime example."""

from oris import Pipeline

pipeline = Pipeline.from_yaml("example.yaml")
result = pipeline.run({"query": "What is AI?"})
print(result.output)
