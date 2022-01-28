# Create your models here.
import re

from django.core.exceptions import ValidationError
from nango.db import models


class Company(models.Model):
    class Meta:
        verbose_name_plural = "companies"
        abstract = False

    name = models.CharField(max_length=100)
    notes = models.TextField()

    def __str__(self) -> str:
        return self.name.title()


RE_BOUNDARY = re.compile(r"[\b\W]+")


def has_vowel_in_each_word(words: str):
    for word in RE_BOUNDARY.split(words.lower()):
        if len(word.strip()) == 0:
            continue
        for vowelish in "aeiouy":
            if vowelish in word:
                break
        else:
            print(f"{word=} does not have a vowel")
            return False
    return True


class Customer(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField()
    company = models.ForeignKey(
        Company, null=True, default=None, on_delete=models.PROTECT
    )

    def clean(self):
        self.name = self.name.title()
        if len(self.name) < 5:
            raise ValidationError({"name": "Too short"})
        if not has_vowel_in_each_word(self.name):
            raise ValidationError({"name": "Each part of the name must have a vowel"})

        self.notes = self.notes.title()
        if len(self.notes) < 5:
            raise ValidationError({"notes": "Too short"})
        if not has_vowel_in_each_word(self.notes):
            raise ValidationError({"notes": "Each word must have a vowel"})
        return super().clean()

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = False
