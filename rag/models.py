from django.db import models
from pgvector.django import VectorField


class DocumentChunk(models.Model):
    source = models.CharField(max_length=255)
    page = models.PositiveIntegerField()
    chunk_index = models.PositiveIntegerField()
    text = models.TextField()
    embedding = VectorField(dimensions=384)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("source", "page", "chunk_index")

    def __str__(self):
        return f"{self.source} p.{self.page} #{self.chunk_index}"