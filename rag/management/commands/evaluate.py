import os

from django.core.management.base import BaseCommand

from rag.retriever import retrieve

# (question, file that should contain the answer). Adjust to what your text files really say.
ON_TOPIC = [
    ("What are the symptoms of dengue?", "who_dengue.txt"),
    ("How is dengue spread?", "who_dengue.txt"),
    ("Is there a specific treatment for dengue?", "who_dengue.txt"),
    ("How can dengue be prevented?", "who_dengue.txt"),
    ("What are the types of diabetes?", "who_diabetes.txt"),
    ("What complications can diabetes cause?", "who_diabetes.txt"),
    ("How can type 2 diabetes be prevented?", "who_diabetes.txt"),
    ("What are the risk factors for high blood pressure?", "who_hypertension.txt"),
    ("How can I reduce my blood pressure?", "who_hypertension.txt"),
    ("What are the complications of hypertension?", "who_hypertension.txt"),
]

OFF_TOPIC = [
    "Who won the cricket world cup?",
    "Best pizza recipe",
    "How do I learn Python?",
    "What is the capital of France?",
]


class Command(BaseCommand):
    help = "Measure retrieval hit rate and off-topic rejection."

    def handle(self, *args, **options):
        threshold = float(os.getenv("MAX_DISTANCE", "0.6"))

        top1 = hit4 = 0
        for question, expected in ON_TOPIC:
            results = retrieve(question, k=4)
            sources = [r["source"] for r in results]
            is_top1 = sources[0] == expected
            is_hit4 = expected in sources
            top1 += is_top1
            hit4 += is_hit4
            self.stdout.write(
                f"{'OK ' if is_hit4 else 'MISS'} d={results[0]['distance']:.3f} "
                f"top1={sources[0]} | {question}"
            )

        rejected = 0
        for question in OFF_TOPIC:
            d = retrieve(question, k=1)[0]["distance"]
            ok = d > threshold
            rejected += ok
            self.stdout.write(f"{'OK ' if ok else 'LEAK'} d={d:.3f} | {question}")

        n = len(ON_TOPIC)
        self.stdout.write(f"\nTop-1 accuracy:  {top1}/{n}")
        self.stdout.write(f"Hit rate (top 4): {hit4}/{n}")
        self.stdout.write(f"Off-topic rejected: {rejected}/{len(OFF_TOPIC)} (threshold {threshold})")