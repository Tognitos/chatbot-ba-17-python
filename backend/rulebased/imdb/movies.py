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

from refo import Plus, Question, Group
from quepy.dsl import HasKeyword
from quepy.parsing import Lemma, Lemmas, Pos, QuestionTemplate, Particle
from dsl import IsMovie, NameOf, IsPerson, IsGenre, IsKeyword, \
    DirectedBy, LabelOf, DurationOf, HasActor, HasName, ReleaseDateOf, \
    DirectorOf, StarsIn, DefinitionOf

nouns = Plus(Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS")| Pos("VBG"))

# TODO: understand what this does!
# TODO: research on internet if there are python query builder
def generate_nodes_tables(definition,tables,columns_target, condition_cols=None, condition_values=None, popular=False, recent=False):

    # are there any conditions (filters)
    addcon=len(condition_cols)>0

    # if there are conditions add them with a like, lowercase
    if addcon:
        definition.nodes = [' lower(a.'+condition_cols[0]+') like "%'+condition_values[0]+'%"']
    else:
        definition.nodes = [' 1=1 ']

    # prepend year filter
    if recent:
        if addcon:
            definition.nodes[0] =  (u' lower(a.'+condition_cols[0]+') like "%'+condition_values[0]+'%"') + u" and  b.year>YEAR(curdate())-2"
        else:
            definition.nodes[0] =  (u" b.year>YEAR(curdate())-2 order by b.year")
    definition.head= u"a."+columns_target[0]

    if  tables[0]=="movies":
        definition.tables = [ tables[0]+u" as a "]
    else:
        definition.tables = [ tables[0]+u" as a left join movies as b on(a.movie_id=b.id) "]
    if popular:
        definition.tables[0] += u"  left join ratings as c on(a.movie_id=c.movie_id)"
        definition.nodes[0] += u" order by (c.votes*c.rank) desc"
    print definition.nodes


class Movie(Particle):
    regex = Question(Pos("DT")) + nouns


    def interpret(self, match):
        name = match.words.tokens
        exp = IsMovie()
        exp.tables = ["movies"]
        return IsMovie() + HasName(name)


class Genre(Particle):
    regex = Question(Pos("DT")) + nouns


    def interpret(self, match):
        name = match.words.tokens
        exp = IsGenre()
        exp.tables = ["genres"]
        return IsGenre() + HasName(name)



class Keyword(Particle):
    regex = Question(Pos("DT")) + nouns


    def interpret(self, match):
        name = match.words.tokens
        exp = IsKeyword()
        exp.tables = ["keywords"]
        return IsGenre() + HasName(name)


class Actor(Particle):
    regex = nouns

    def interpret(self, match):
        name = match.words.tokens
        exp = IsPerson()
        exp.tables = ["actors", "actresses"]


        return exp + HasKeyword(name)


class Director(Particle):
    regex = nouns

    def interpret(self, match):
        name = match.words.tokens
        exp=IsPerson()
        exp.tables = ["directors"]
        return exp + HasKeyword(name)


class ListMoviesQuestion(QuestionTemplate):
    """
    Ex: "list movies"
    """
    prob_threshold = 0.95
    tables = ["movies","genre"]
    examples = [ "list movies", "list popular movies"]
    examples_entities = [ "list <modifier>popular</modifier> <genre>action</genre> movies"]

    # You must have an attribute called 'regex'
    # The Group option matches a movie object or a POS (e.g. POS(NN)) and associates it to the "target" name. This will create match.target object
    regex = Lemma("list") +Question(Lemma("recent")) +Question(Lemma("popular"))+ Question(Genre())+ Group(Movie(), "target")#(Lemma("movie") | Lemma("film"))


    """
    match obj in case of 'list movies' :
    {'_words': [list|list|NN|None, movies|movie|NNS|None], '_particles': {}, '_match': <refo.match.Match object at 0x7f2f1ab1f3d0>, '_j': None, '_i': None}

    match obj in case of 'lists movies' :
    {'_words': [lists|list|NNS|None, movies|movie|NNS|None], '_particles': {}, '_match': <refo.match.Match object at 0x7f2f1ab1f3d0>, '_j': None, '_i': None}

    As you can see in the second example, what changes is the words matched.
    It defines that the word lists (plural) was matched, lemmatized to list (singular general form), and it was a NNS form (plural) instead of NN (singular) at the time of the match.

    The other word matched was 'movies', lemmatized to 'movie', was a POS-tag NNS (plural) at the time of the match.
    """

    def interpret(self, match):
        print('match')
        print(match.__dict__)

        print('match._match')
        print(match._match.__dict__)

        print('match.target')
        print(match.target.__dict__)

        # match.target exists just because of the Group(Movie(), "target")
        print('match.target.tokens')
        print(match.target.tokens)

        print('haskeyword')
        print(HasKeyword(match.target.tokens).__dict__)

        movie = IsMovie()
        movie_name = NameOf(movie)

        """
        {'nodes': [[(u'rdf:type', u'dbpedia-owl:Film'), ('foaf:name', 1)]], 'fixedtyperelation': u'rdf:type', 'head': 0, 'fixedtype': u'dbpedia-owl:Film'}
        """
        print('movie (ismovie)')
        print(movie.__dict__)

        """
        {'nodes': [[(u'rdf:type', u'dbpedia-owl:Film'), ('foaf:name', 1)], []], 'head': 1}
        """
        print('moviename (nameof(ismovie))')
        print(movie_name.__dict__)

        print('words are classes, not just simple texts')
        first_word = match.words[0] # {'lemma': u'list', 'token': u'list', 'pos': u'NN', 'prob': None}
        second_word = match.words[1] # {'lemma': u'movie', 'token': u'movies', 'pos': u'NNS', 'prob': None}
        print('first word')
        print(first_word.__dict__)
        print('second word')
        print(second_word.__dict__)

        print(match.target.tokens)

        matched_lemmas = [k.lemma for k in match.words]
        recent= u"recent" in matched_lemmas
        popular= u"popular" in matched_lemmas

        select_expressions = ["title"]

        if hasattr(match, 'genre'):
            tables=[u"genres"]
            condition_cols=[u"genre"]
            condition_values=[''.join(match.genre.nodes[0][1][1].split('"')[:-1])]
        else:
            tables=[u"title"]
            condition_cols=[]
            condition_values=[]
        generate_nodes_tables(movie_name, tables, select_expressions, condition_cols=condition_cols, condition_values=condition_values, popular=popular, recent=recent)
        movie_name.nodes[0] +=  " limit 10" #[u'title like "'+match.movie+'"']
        print "nodes",movie_name.nodes
        print movie_name
        return movie_name, ("enum","ListMoviesQuestion")


class MoviesByDirectorQuestion(QuestionTemplate):
    """
    Ex: "List movies directed by Quentin Tarantino.
        "movies directed by Martin Scorsese"
        "which movies did Mel Gibson directed"
    """
    prob_threshold = 0.95
    tables = ["movies","directors"]

    examples = [ "List movies directed by Quentin Tarantino.",
                 "movies directed by Martin Scorsese",
                 "which movies did Mel Gibson directed"]
    examples_entities = [ "list movies <ckeyword>directed</ckeyword> by <director>Quentin Tarantino</director> "]

    regex = (Question(Lemma("list")) + (Lemma("movie") | Lemma("film")) +
             Question(Lemma("direct")) + Lemma("by") + Director()) | \
            (Lemma("which") + (Lemma("movie") | Lemma("film")) + Lemma("do") +
             Director() + Lemma("direct") + Question(Pos(".")))

    def interpret(self, match):
        #print(dir(match), match.director, match.words)
        #movie = IsMovie() + DirectedBy(match.director)
        #movie_name = LabelOf(movie)
        #use only the name of the director
        name_dir=''.join(match.director.nodes[0][1][1].split('"')[:-1])
        names =name_dir.split()
        movie_name=IsPerson()
        if len(names)==1:
            movie_name.nodes = [u' name like "'+names+'"']
        else:
            movie_name.nodes = [u' name like "'+u" ".join(names[:-1])+
                            u'" and surname like "'+names[-1]+'"']
        movie_name.tables = [u"directors"]
        movie_name.head= u"title"

        return movie_name, ("enum", "MoviesByDirectorQuestion")


class MovieDurationQuestion(QuestionTemplate):
    """
    Ex: "How long is Pulp Fiction"
        "What is the duration of The Thin Red Line?"
    """
    prob_threshold = 0.95
    tables = [ "movies"]
    examples = [ "How long is Pulp Fiction",
                 "What is the duration of The Thin Red Line?"]

    regex = ((Lemmas("how long be") + Movie()) |
            (Lemmas("what be") + Pos("DT") + Lemma("duration") +
             Pos("IN") + Movie())) + \
            Question(Pos("."))

    def interpret(self, match):
        duration = DurationOf(match.movie)
        duration.tables = ["movies"]
        return duration, ("literal", "{} minutes long")


class ActedOnQuestion(QuestionTemplate):
    """
    Ex: "List movies with Hugh Laurie"
        "Movies with Matt LeBlanc"
        "In what movies did Jennifer Aniston appear?"
        "Which movies did Mel Gibson starred?"
        "Movies starring Winona Ryder"
    """
    prob_threshold = 0.95
    tables =  [ "actors","actresses"]
    examples = ["List movies with Hugh Laurie",
                "Movies with Matt LeBlanc",
                "In what movies did Jennifer Aniston appear?",
                "Which movies did Mel Gibson starred?",
                "Movies starring Winona Ryder"]

    acted_on = (Lemma("appear") | Lemma("act") | Lemma("star") | Lemmas("play in"))
    movie = Question(Lemma("recent"))+(Lemma("movie") | Lemma("movies") | Lemma("film"))
    regex = (Question(Lemma("list")) + movie + Lemma("with") + Actor()) | \
            (Question(Pos("IN")) + (Lemma("what") | Lemma("which")) +
             movie + Lemma("do") + Actor() + acted_on + Question(Pos("."))) | \
            (Question(Pos("IN")) + Lemma("which") + movie + Lemma("do") +
             Actor() + acted_on) | \
            (Question(Lemma("list")) + movie + Lemma("star") + Actor())|\
            Question(Lemmas("i would like to see"))+movie+ Lemma("with") +\
            Actor()+ Question(Pos("."))

    def interpret(self, match):
        movie = IsMovie() + HasActor(match.actor)
        movie_name = NameOf(movie)
        name_dir=''.join(match.actor.nodes[0][1][1].split('"')[:-1])
        names =name_dir.split()
        if  u"recent" in [k.lemma for k in match.words]:
            movie_name.head = "a.name,a.surname,a.title"

            if len(names)==1:
                movie_name.nodes = [u' name like "'+names+'" and  b.year>YEAR(curdate())-2']
            else:
                movie_name.nodes = [u' name like "'+u" ".join(names[:-1])+
                                u'" and surname like "'+names[-1]+'" and  b.year>YEAR(curdate())-2']
            movie_name.head= u"a.title"
            movie_name.tables = ["actors as a left join movies as b on(a.movie_id=b.id) ","actresses as a left join movies as b on(a.movie_id=b.id) "]
            #print("definition ",definition)

        else:
            movie_name.tables = ["actors", "actresses"]
            movie_name.head = "title,name,surname"
            if len(names)==1:
                movie_name.nodes = [u' name like "'+names+'"']
            else:
                movie_name.nodes = [u' name like "'+u" ".join(names[:-1])+
                                u'" and surname like "'+names[-1]+'"']
        return movie_name, ("enum", "ActedOnQuestion")


class MovieReleaseDateQuestion(QuestionTemplate):
    """
    Ex: "When was The Red Thin Line released?"
        "Release date of The Empire Strikes Back"
    """

    prob_threshold = 0.95
    tables = ["movies"]
    examples = ["When was The Red Thin Line released?",
                "Release date of The Empire Strikes Back"]

    regex = ((Lemmas("when be") + Movie() + Lemma("release")) |
            (Lemma("release") + Question(Lemma("date")) +
             Pos("IN") + Movie())) + \
            Question(Pos("."))

    def interpret(self, match):
        release_date = ReleaseDateOf(match.movie)
        release_date.tables = ["movies"]
        movie_name=''.join(match.movie.nodes[0][1][1].split('"')[:-1])
        release_date.nodes = [u' title like "'+movie_name+'"']
        release_date.head= u"year"
        return release_date, ("literal","MovieReleaseDateQuestion")


class DirectorOfQuestion(QuestionTemplate):
    """
    Ex: "Who is the director of Big Fish?"
        "who directed Pocahontas?"
    """
    prob_threshold = 0.95
    tables  = ["directors"]
    examples = ["Who is the director of Big Fish?",
                "who directed Pocahontas?"]

    regex = ((Lemmas("who be") + Pos("DT") + Lemma("director") +
             Pos("IN") + Movie()) |
             (Lemma("who") + Lemma("direct") + Movie())) + \
            Question(Pos("."))

    def interpret(self, match):
        director_name = IsPerson()
        movie_name=''.join(match.movie.nodes[0][1][1].split('"')[:-1])
        director_name.nodes = [u' title like "%'+movie_name+'%"']
        director_name.tables = [u"directors"]
        director_name.head= u"name,surname,title "
        #director = IsPerson() + DirectorOf(match.movie)
        #director_name = NameOf(director)
        director_name.tables = ["directors"]
        return director_name, ("literal","DirectorOfQuestion")


class ActorsOfQuestion(QuestionTemplate):
    """
    Ex: "who are the actors of Titanic?"
        "who acted in Alien?"
        "who starred in The Predator?"
        "Actors of Fight Club"
    """
    prob_threshold = 0.95
    tables = ["actors","actresses"]
    examples = ["who are the actors of Titanic?"
                "who acted in Alien?",
                "who starred in Depredator?",
                "Actors of Fight Club"]

    regex = (Lemma("who") + Question(Lemma("be") + Pos("DT")) +
             (Lemma("act") | Lemma("actor") | Lemma("star")) +
             Pos("IN") + Movie() + Question(Pos("."))) | \
            ((Lemma("actors") | Lemma("actor")) + Pos("IN") + Movie())

    def interpret(self, match):
        actor = IsPerson()
        movie_name=''.join(match.movie.nodes[0][1][1].split('"')[:-1])
        actor.nodes = [u' title like "%'+movie_name+'%"']
        actor.tables = ["actors", "actresses"]
        actor.head= u"name,surname,title"
        return actor, ("enum","ActorsOfQuestion")


class PlotOfQuestion(QuestionTemplate):
    """
    Ex: "what is Shame about?"
        "plot of Titanic"
    """
    prob_threshold = 0.95
    tables = ["plot"]
    examples = [ "what is Shame about?",
                 "plot of Titanic"]
#Lemmas("what be") + Movie() + Lemma("about")  + Question(Pos("."))
    regex = ((Lemmas("what be") + Movie() + Lemma("about")) | \
             (Question(Lemmas("what be the")) + Lemma("plot") +
              Pos("IN") + Movie()))  \
            + Question(Pos("."))

    def interpret(self, match):
        print("halllo")
        definition = DefinitionOf(match.movie)
        #print("Match ",match.movie)
        movie_name=''.join(match.movie.nodes[0][1][1].split('"')[:-1])
        definition.nodes = [u' title like "%'+movie_name+'%"']
        definition.head= u"plot"
        definition.tables = ["plot"]
        #print("definition ",definition)
        return definition, ("define","PlotOfQuestion")



class RecentMoviesKeyQuestion(QuestionTemplate):
    """
    Ex: "Show me recent action movies?"
    Tonight I feel like watching a recent action movie
    List popular   action movies
    """
    prob_threshold = 0.95
    tables = ["genres","movies","keywords"]
    #todo left join with ratings for popularity
    examples = ["Show me recent action movies?",
                "Tonight I feel like watching a recent action movie",
                "List popular   action movies"]

    regex =  (Lemmas("show me") |Lemma("list") |\
             (Question(Lemmas("tonight i feel like")) + Lemma("watch"))) + \
     Question( Pos("DT")) + \
    Question(Lemma("recent"))+Question(Lemma("popular"))+\
    Genre() + Lemma("movie") + Question(Pos("."))


    def interpret(self, match):
        definition = DefinitionOf(match.genre)
        #print("Match ",dir(match))
        matched_lemmas = [k.lemma for k in match.words]
        recent= u"recent" in matched_lemmas
        popular= u"popular"  in matched_lemmas
        if recent or popular:

            genre_name=''.join(match.genre.nodes[0][1][1].split('"')[:-1])
            generate_nodes_tables(definition,["genres"], ["title"], condition_cols=["genre"], condition_values=[genre_name], popular=popular, recent=recent)
            #definition.nodes = [u' lower(a.genre) like "%'+genre_name+'%" and  b.year>YEAR(curdate())-2']
            #definition.head= u"a.title"
            #definition.tables = ["genres as a left join movies as b on(a.movie_id=b.id) "]
            #print("definition ",definition)

        else:
            genre_name=''.join(match.genre.nodes[0][1][1].split('"')[:-1])
            definition.nodes = [u' lower(genre) like "%'+genre_name+'%"']
            definition.head= u"title"
            definition.tables = ["genres"]
            #print("definition ",definition)
        return definition, ("define","RecentMoviesKeyQuestion")




class MoviesKeywordQuestion(QuestionTemplate):
    """
    Ex: "I'm in the mood for a samurai story"
        "Show me samurai movies"
        "List kung-fu movies"
    """
    prob_threshold = 0.95
    #todo left join with ratings for popularity
    examples = ["I'm in the mood for a samurai story",
                "Show me samurai movies",
                "List kung-fu movies"]

    tables = ["genres","keywords","movies"]

    regex =  ((Lemmas("show me") |\
             (Question(Lemmas("tonight i feel like")) + Lemma("watch"))) + \
     Question( Pos("DT")) + \
    Question(Lemma("recent"))+Keyword() + Lemma("movie") + Question(Pos(".")))|\
              (Question(Lemmas("i ' m in the mood for a")) + Keyword() + \
               (Question(Lemma("story"))|Question(Lemma("movie")))+ \
                Question(Pos(".")))

    def interpret(self, match):
        definition = DefinitionOf(match.keyword)
        print('aaa')
        #print("Match ",dir(match))
        #print (match.words)
        #print (match.keyword.nodes)
        if  u"recent" in [k.lemma for k in match.words]:

            keyword_name=''.join(match.keyword.nodes[0][1][1].split('"')[:-1])
            if keyword_name.find(" ")>-1:
                definition.nodes = [u' lower(a.keyword) like "%'+'%" or lower(keyword) like "%'.join(keyword_name.split())+'%" and  b.year>YEAR(curdate())-2']
            else:
                definition.nodes = [u'lower(a.keyword) like "%'+ keyword_name+'%"  and  b.year>YEAR(curdate())-2']
            definition.head= u"a.title"
            definition.tables = ["keywords as a left join movies as b on(a.movie_id=b.id) "]
            #print("definition ",definition)

        else:
            keyword_name=''.join(match.keyword.nodes[0][1][1].split('"')[:-1])
            if keyword_name.find(" ")>-1:
                definition.nodes = [u'lower(keyword) like "%'+ u'%" or lower(keyword) like "%'.join(keyword_name.split())+u'%"']
            else:
                definition.nodes = [u'lower(keyword) like "%'+ keyword_name +u'%"']
            print definition.nodes
            definition.head= u"title"
            definition.tables = ["keywords"]
            #print("definition ",definition)
        return definition, ("define","MoviesKeywordQuestion")

# By Matteo, not very useful
class WhoIsActorQuestion(QuestionTemplate):
    """
    Ex: "Who is Michelle Pfeiffer?"
    """
    prob_threshold = 0.95

    examples = ["Who is Michelle Pfeiffer?"]

    tables = ["actors","actresses"]

    regex = (
                (
                    Lemmas("who be") + Question(Pos("DT")) + Actor() \
                )
            ) \
            + Question(Pos("."))

    def interpret(self, match):
        definition = DefinitionOf(match.actor)
        #print("Match ",match.movie)
        actor_name=''.join(match.actor.nodes[0][1][1].split('"')[:-1])
        print("Actor name ", actor_name)
        definition.nodes = [u' concat(name, " ", surname) like concat("%", replace("' + actor_name + '", " ", "%"), "%")']
        # what to extract
        definition.head= u" distinct name, surname, title"
        definition.tables = ["actors","actresses"]
        #print("definition ",definition)
        return definition, ("define","WhoIsActorQuestion")
