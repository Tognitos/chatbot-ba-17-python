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
from quepy.dsl import HasKeyword
from quepy.parsing import Lemma, Lemmas, Pos, QuestionTemplate, Particle, Group, Literal
from dsl import IsMovie, NameOf, IsPerson, IsGenre, IsKeyword, \
    DirectedBy, LabelOf, LabelOfReversed, DurationOf, HasActor, HasName, \
    ReleaseDateOf, DirectorOf, StarsIn, DefinitionOf, PlotOf, CounterOf
from movie_particles import *
from utils import MyExtra, OrderBy, replace_prop

class ListMoviesQuestion(QuestionTemplate):
    """
    Ex: "list movies"
    """

    regex = Lemma("list") + (Lemma("movie") | Lemma("film"))

    def interpret(self, match):
        movie = IsMovie()
        name = NameOf(movie)
        return name, "enum"


class MovieReleaseDateQuestion(QuestionTemplate):
    """
    Ex: "When was The Red Thin Line released?"
        "Release date of The Empire Strikes Back"
    """

    regex = ((Lemmas("when be") + Movie() + Lemma("release")) |
            (Lemma("release") + Question(Lemma("date")) +
             Pos("IN") + Movie())) + \
            Question(Pos("."))

    def interpret(self, match):
        release_date = ReleaseDateOf(match.movie)
        return release_date, "literal"

class MovieRecentReleaseDateGenreQuestion(QuestionTemplate):
    """
    Ex: "Show me  recent action movie"
        "Show me  recent genre movie"

    """
    # TODO remove this? The following regex matches something cocmpletely different (already done in tognimat.py)
    regex = ((Lemmas("Show me") + Lemma("release")) |
            (Lemma("release") + Question(Lemma("date")) +
             Pos("IN") + Movie())) + \
            Question(Pos("."))

    def interpret(self, match):
        release_date = ReleaseDateOf(match.movie)
        return release_date, "literal"

class PlotOfQuestion(QuestionTemplate):
    """
    Ex: "what is (the movie/film) Shame about(?)"
        "what is the plot/story of Shame(?)"
        "plot of Titanic"
    """

    regex1 = Lemmas("what be") + \
             Question(Literal("the") + (Lemma("movie") | Lemma("film"))) + \
             Movie() + Question(Lemma("about")) +  Question(Pos("."))

    regex = regex1

    def interpret(self, match):
        match.movie.add_data(u"dbpprop:counter",u"?counter")
        plot = PlotOf(match.movie)
        #plot.add_data(u"dbpprop:counter",u"?counter")
        old_value = replace_prop(plot, u"dbpprop:name", u"?name")
        #replace_prop(plot,u"dbpprop:plot", u"?plot")

        extra = MyExtra('FILTER regex(?name, "%s", "i").' % old_value)
        plot.add_data(extra,u"")
        #plot.add_data(OrderBy("DESC(xsd:integer(?counter))"),u"")
        #plot.head = "*"
        return plot, "list"
