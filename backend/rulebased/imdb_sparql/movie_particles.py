# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Movie related regex.
"""

from refo import Plus, Question
from quepy.parsing import Pos, Particle, Lemma, Lemmas

# relations
from dsl import IsMovie, NameOf, IsPerson, IsGenre, IsKeyword, \
    DirectedBy, LabelOf, LabelOfReversed, DurationOf, HasActor, HasName, \
    ReleaseDateOf, DirectorOf, StarsIn, DefinitionOf, IsActor, HasKeyword, \
    IsDirector

nouns = Plus(Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS"))
movie_lemmas = (Lemma("movie") | Lemma("story") | Lemma("film"))


## PARTICLES


class Movie(Particle):
    regex = Question(Pos("DT")) + Plus(nouns | Pos("JJ"))

    def interpret(self, match):
        name = match.words.tokens
        return IsMovie() + HasName(name)

class Genre(Particle):
    regex = Question(Pos("DT")) + nouns

    def interpret(self, match):
        name = match.words.tokens
        exp = IsGenre()
        return IsGenre() + HasName(name)

class Actor(Particle):
    regex = nouns

    def interpret(self, match):
        name = match.words.tokens
        return IsActor() + HasName(name)

class Director(Particle):
    regex = nouns

    def interpret(self, match):
        name = match.words.tokens
        return IsDirector() + HasName(name)

class Keyword(Particle):
    # nouns | foreign words | adjectives (non comparative, non superlative!)
    regex = Question(Pos("DT")) + (nouns | Pos("FW") | Pos("JJ"))

    def interpret(self, match):
        name = match.words.tokens
        return IsKeyword() + HasName(name)


## END OF ENTITIES
