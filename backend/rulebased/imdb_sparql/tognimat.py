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
from quepy.parsing import Lemma, Lemmas, Pos, QuestionTemplate, Particle, Literal

# relations
from dsl import IsMovie, NameOf, IsPerson, IsGenre, IsKeyword, \
    DirectedBy, LabelOf, LabelOfReversed, DurationOf, HasActor, HasName, \
    ReleaseDateOf, DirectorOf, StarsIn, DefinitionOf, IsActor, IsDirector, \
    Follows

# particles
from movie_particles import Movie, Actor, Director, Keyword, Genre

nouns = Plus(Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS"))
movie_lemmas = (Lemma("movie") | Lemma("story") | Lemma("film"))
maybe_dot_or_qmark = Question(Pos(".") | Pos("?"))


class MoviesByDirectorQuestion(QuestionTemplate):
    """
    Ex: "List movies directed by Quentin Tarantino.         # ok
        "movies directed by Martin Scorsese"                # ok
        "list movies that Clint Eastwood directed."          # ok
        "list movies that Clint Eastwood has directed"      # ok
        "list movies that Clint Eastwood did direct"        # ok
        "list movies directed by Steven Spielberg"          # ok
        "list movies by Steven Spielberg"                   # ok
        "list movies of Steven Spielberg"                   # ok
        "movies by Steven Spielberg"                        # ok
        "which movies did Mel Gibson direct"                # ok
        "which movies has Mel Gibson directed"              # ok
    """

    direct = Lemma("direct")
    maybe_list = Question(Lemma("list"))
    
    regex1 = maybe_list + (movie_lemmas) + Question(direct) + Lemma("by") + Director()
    regex2 = Lemma("which") + (movie_lemmas) + (Lemma("do") | Lemma("have")) + Director() + direct
    regex3 = maybe_list + (movie_lemmas) + Lemma("that") + Director() + Question(Lemma("do") | Lemma("have")) + direct
    regex4 = maybe_list + (movie_lemmas) + Question(direct) + (Lemma("by") | Lemma("of")) + Director()
    
    regex = (regex1 | regex2 | regex3 | regex4) \
            + maybe_dot_or_qmark
            
    def interpret(self, match):
        #print(dir(match), match.director, match.words)
        movie = IsMovie() + DirectedBy(match.director)
        
        movie_name = NameOf(movie)
        print(movie_name)
        return movie_name, "enum"


class MovieDurationQuestion(QuestionTemplate):
    """
    Ex: "How long is Pulp Fiction"                      # ok
        "How long is Pulp Fiction?"                     # ok
        "What is the duration of The thin Red Line?"    # ok
        "What is the duration of the thin red line?"    # not ok
        "What is the duration of "the thin red line"?"  # not ok
    """
    
    duration = Lemma("duration") | Lemma("length")
    
    regex1 = Lemmas("how long be") + Movie()
    regex2 = Lemmas("what be") + Pos("DT") + duration + Lemma("of") + Movie()
    regex3 = duration + Lemma("of") + Movie()
    
    regex = (regex1 | regex2 | regex3) \
            + maybe_dot_or_qmark

    def interpret(self, match):
        duration = DurationOf(match.movie)
        print(duration.__dict__)
        return duration, ("literal", "{} minutes long")


class ActedOnQuestion(QuestionTemplate):
    """
    Ex: "List movies with Hugh Laurie"                      # ok
        "Movies with Matt LeBlanc"                          # not ok: yes, the problem is the big "M" (lemmatizer should do it already or not??)
        "movies with Matt LeBlanc"                          # ok
        "In what movies did Jennifer Aniston appear?"       # ok
        "Which movies did Mel Gibson starred?"              # ok
        "Movies starring Winona Ryder"                      # not ok
        movies where Matt LeBlanc starred                   # ok
        movies in which Matt LeBlanc played in              # ok
        list movies in which Matt LeBlanc appears           # ok
    """
    
    maybe_list = Question(Lemma("list") | Lemma("elencate") | Lemmas("spell out") + Lemmas("write down") + Lemmas("tell me the"))
    acted_on = (Lemma("appear") | Lemma("act") | Lemma("star") | Lemmas("play in"))
    
    regex1 = maybe_list + movie_lemmas + Lemma("with") + Actor()
    regex2 = maybe_list + Question(Pos("IN")) + (Lemma("what") | Lemma("which")) + movie_lemmas + (Lemma("do") | Lemma("have")) + Actor() + acted_on
    regex3 = maybe_list + movie_lemmas + (Lemma("where") | Lemmas("in which")) + Actor() + acted_on
    
    regex = (regex1 | regex2 | regex3) \
            + maybe_dot_or_qmark

    def interpret(self, match):
        movie = IsMovie() + HasActor(match.actor)
        movie_name = NameOf(movie)
        print(movie_name.__dict__)
        return movie_name, "enum"

class ActorsOfQuestion(QuestionTemplate):
    """
    Ex: "who are the actors of Titanic?"    # ok
        "who acted in Alien?"               # ok
        "who starred in Depredator?"        # ok
        "who starred in Depredator"         # ok
        "actors of Fight Club"              # ok
        list actors of Mulan
    """
    who = Lemma("who")
    act_verb = (Lemma("star") | Lemma("act") | Lemma("feature"))
    actor = (Lemma("actor") | Lemma("actors"))
    maybe_list = Question(Lemma("list"))
    
    regex1 = who + Lemma("be") + Pos("DT") + Lemma("actor") + Pos("IN") + Movie()
    regex2 = who + act_verb + Pos("IN") + Movie()
    regex3 = maybe_list + actor + Pos("IN") + Movie()
    
    regex = (regex1 | regex2 | regex3) \
            + maybe_dot_or_qmark

    def interpret(self, match):
        actor = NameOf(IsPerson() + StarsIn(match.movie))
        print(actor)
        return actor, "enum"

# Looks for the keywords ("tags") in the movies.
class MoviesKeywordQuestion(QuestionTemplate):
    """
    Ex: "I'm in the mood for a samurai story"                   # not ok
        "Show me samurai movies"                                # ok
        "List samurai movies"                                   # ok
        "Tonight I feel like (watching) (a) samurai movie"      # ok
    """
    #prob_threshold = 0.95

    movie_lemmas = (Lemma("movie") | Lemma("story") | Lemma("film"))
    show_me = (Lemmas("show me") | Lemma("list"))
    
    regex1 = show_me + Keyword() + movie_lemmas
    regex2 = (Lemmas("tonight i feel like") + Question(Lemma("watch"))) + Question(Pos("DT")) +  Keyword() + movie_lemmas
    
    regex = (regex1 | regex2) \
            + maybe_dot_or_qmark

    def interpret(self, match):
        movie_names = NameOf(LabelOf(match.keyword))
        print(movie_names)
        return movie_names, ("define","MoviesKeywordQuestion")
        
class DirectorOfQuestion(QuestionTemplate):
    """
    Ex: "Who is the director of Big Fish?"      # ok
        "who directed Pocahontas?"              # ok
        director of Sparta?                     # ok
        tell me who directed Nemo                   # ok
        tell me who is the director of Gran Torino  # ok, grammatically wrong
    """

    who = Lemma("who")
    director = Lemma("director")
    maybe_tellme = Question(Lemmas("tell me"))
    
    regex1 = maybe_tellme + Question(who + Lemma("be") + Pos("DT") + director) + Pos("IN") + Movie()
    regex2 = maybe_tellme + who + Lemma("direct") + Movie()
    regex3 = director + Pos("IN") + Movie()
    
    regex = (regex1 | regex2 | regex3) \
            + maybe_dot_or_qmark


    def interpret(self, match):
        director = IsDirector() + DirectorOf(match.movie)
        director_name = NameOf(director)
        return director_name, "literal"
        
        
class MovieReleaseDateQuestion(QuestionTemplate):
    """
    Ex: "Show me release date of Pocahontas"    # ok
        show me release date of Pocahontas      # ok
        release date of Bambi                   # ok
        release date of Bambi?                  # ok
        the release date of Bambi?              # ok
        "Tell me the release date of Bambi"     # ok
        when was Big Fish released?             # ok

    """
    tellme = Question(Lemmas("show me") | Lemmas("tell me"))
    maybe_the = Question(Lemma("the"))
    release_date = Lemmas("release date")
    
    regex1 = tellme + maybe_the + release_date + Pos("IN") + Movie()
    regex2 = Lemma("when") + Lemma("be") + Movie() + Lemma("release")
    
    regex = (regex1 | regex2) \
            + maybe_dot_or_qmark


    def interpret(self, match):
        release_date = ReleaseDateOf(match.movie)
        print(release_date)
        return release_date, "literal"
        

        
class MovieFollowsQuestion(QuestionTemplate):
    """
    Ex: sequels of Big Fish
    """
    tellme = Question(Lemma("show") | Lemmas("show me") | Lemmas("tell me") | Lemma("list"))
    maybe_the = Question(Lemma("the"))
    sequels = Lemma("spin-off") | Lemma("sequel")
    
    regex1 = tellme + maybe_the + sequels + Pos("IN") + Movie()
    
    regex = (regex1) \
            + maybe_dot_or_qmark


    def interpret(self, match):
        movie_name = NameOf(Follows(match.movie))
        
        print(movie_name)
        return movie_name, "enum"
        

