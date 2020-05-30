import ast
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os

studentid = os.path.basename(sys.modules[__name__].__file__)

#################################################
# Your personal methods can be here ...


def func_q8_2(data):
    if isinstance(data, list):
        res = list()
        for i in range(len(data)):
            cast = data[i]
            res.append(cast['character'])
        res = sorted(res)
        return ','.join(res)


def func_q9(data):
    if data:
        return len(data.split(","))


def func_q11_2(data):
    if isinstance(data, list):
        res = list()
        for i in range(len(data)):
            cast = data[i]
            res.append(cast['name'])
        return ','.join(res)

#################################################


def log(question, output_df, other):
    print("--------------- {}----------------".format(question))
    if other is not None:
        print(question, other)
    if output_df is not None:
        print(output_df.head(5).to_string())


def question_1(movies, credits):
    """
    :param movies: the path for the movie.csv file
    :param credits: the path for the credits.csv file
    :return: df1
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...

    movies_df = pd.read_csv(movies)
    credits_df = pd.read_csv(credits)
    df1 = pd.merge(movies_df, credits_df, how='left',
                   left_on=['id'], right_on=['id'])

    #################################################

    log("QUESTION 1", output_df=df1, other=df1.shape)
    return df1


def question_2(df1):
    """
    :param df1: the dataframe created in question 1
    :return: df2
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...

    df2 = df1[['id', 'title', 'popularity', 'cast', 'crew', 'budget', 'genres', 'original_language', 'production_companies',
               'production_countries', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'vote_average', 'vote_count']]

    #################################################

    log("QUESTION 2", output_df=df2, other=(
        len(df2.columns), sorted(df2.columns)))
    return df2


def question_3(df2):
    """
    :param df2: the dataframe created in question 2
    :return: df3
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...

    df3 = df2.set_index('id')

    #################################################

    log("QUESTION 3", output_df=df3, other=df3.index.name)
    return df3


def question_4(df3):
    """
    :param df3: the dataframe created in question 3
    :return: df4
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...

    df4 = df3.drop(df3[df3.budget == 0].index)

    #################################################

    log("QUESTION 4", output_df=df4, other=(
        df4['budget'].min(), df4['budget'].max(), df4['budget'].mean()))
    return df4


def question_5(df4):
    """
    :param df4: the dataframe created in question 4
    :return: df5
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...

    df5 = df4.copy()
    df5['success_impact'] = df5.eval('(revenue - budget)/budget')

    #################################################

    log("QUESTION 5", output_df=df5,
        other=(df5['success_impact'].min(), df5['success_impact'].max(), df5['success_impact'].mean()))
    return df5


def question_6(df5):
    """
    :param df5: the dataframe created in question 5
    :return: df6
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...

    df6 = df5.copy()
    minVal = df6['popularity'].min()
    maxVal = df6['popularity'].max()
    df6['popularity'] = ((df6['popularity'] - minVal) /
                         (maxVal - minVal)) * 100

    #################################################

    log("QUESTION 6", output_df=df6, other=(
        df6['popularity'].min(), df6['popularity'].max(), df6['popularity'].mean()))
    return df6


def question_7(df6):
    """
    :param df6: the dataframe created in question 6
    :return: df7
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...

    df7 = df6.copy()
    df7['popularity'] = df7['popularity'].astype('int16')

    #################################################

    log("QUESTION 7", output_df=df7, other=df7['popularity'].dtype)
    return df7


def question_8(df7):
    """
    :param df7: the dataframe created in question 7
    :return: df8
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """
    #################################################
    # Your code goes here ...

    df8 = df7.copy()
    df8['cast'] = df8['cast'].astype('str')
    df8['cast'] = df8['cast'].apply(
        lambda data: ast.literal_eval(data) if data != 'nan' else data)
    df8['cast'] = df8['cast'].apply(func_q8_2)

    #################################################

    log("QUESTION 8", output_df=df8, other=df8["cast"].head(10).values)
    return df8


def question_9(df8):
    """
    :param df9: the dataframe created in question 8
    :return: movies
            Data Type: List of strings (movie titles)
            Please read the assignment specs to know how to create the output
    """
    #################################################
    # Your code goes here ...

    df9 = df8.copy()
    df9['total_charaters'] = df9['cast'].apply(func_q9)
    df9 = df9.sort_values(by=['total_charaters'], ascending=False)
    movies = list(df9['title'].head(10))

    #################################################

    return movies


def question_10(df8):
    """
    :param df8: the dataframe created in question 8
    :return: df10
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...

    df10 = df8.copy()
    df10['release_date'] = pd.to_datetime(df10['release_date'], dayfirst=True)
    df10 = df10.sort_values(by='release_date', ascending=False)

    #################################################

    log("QUESTION 10", output_df=df10, other=df10["release_date"].head(
        5).to_string().replace("\n", " "))
    return df10


def question_11(df10):
    """
    :param df10: the dataframe created in question 10
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    # Your code goes here ...

    df11 = df8.copy()
    df11['genres'] = df11['genres'].astype('str')
    df11['genres'] = df11['genres'].apply(
        lambda data: ast.literal_eval(data) if data != 'nan' else data)
    df11['genres'] = df11['genres'].apply(func_q11_2)
    no_of_rows_to_merge = 4
    df11 = pd.DataFrame(df11['genres'].str.split(',').tolist(
    ), index=df11['title']).stack().reset_index(drop=True)
    new_df = pd.DataFrame({'Genres': df11.value_counts(
    ).keys().tolist(), 'Count': df11.value_counts().tolist()})
    last_rows_sum = new_df.tail(no_of_rows_to_merge)['Count'].sum()
    new_df.drop(new_df.tail(no_of_rows_to_merge).index, inplace=True)
    new_df = new_df.append(
        {"Genres": "other genres", "Count": last_rows_sum}, ignore_index=True)
    _, ax1 = plt.subplots()
    ax1.pie(new_df['Count'], labels=new_df['Genres'],
            autopct='%1.1f%%', pctdistance=0.85, labeldistance=1.05)
    plt.title("Genre", pad=20)
    ax1.axis('equal')
    plt.tight_layout()

    #################################################

    plt.savefig("{}-Q11.png".format(studentid))
    plt.clf()


def question_12(df10):
    """
    :param df10: the dataframe created in question 10
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    # Your code goes here ...

    df12 = df10.copy()
    df12['production_countries'] = df12['production_countries'].astype('str')
    df12['production_countries'] = df12['production_countries'].apply(
        lambda data: ast.literal_eval(data) if data != 'nan' else data)
    df12['production_countries'] = df12['production_countries'].apply(
        func_q11_2)
    df12 = pd.DataFrame(df12['production_countries'].str.split(
        ',').tolist()).stack().reset_index(drop=True)
    new_df = pd.DataFrame({'Countries': df12.value_counts(
    ).keys().tolist(), 'Count of movies': df12.value_counts().tolist()})
    new_df = new_df.sort_values(by='Countries')
    new_df.plot.bar(x='Countries', y='Count of movies',
                    title='Production Country', figsize=(10, 10))
    plt.tight_layout()

    #################################################

    plt.savefig("{}-Q12.png".format(studentid))
    plt.clf()


def question_13(df10):
    """
    :param df10: the dataframe created in question 10
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    # Your code goes here ...

    df13 = df10.copy()
    unique_lang = df13['original_language'].unique()
    color = 0
    first = True
    red = np.random.rand(len(unique_lang) + 1)
    green = np.random.rand(len(unique_lang) + 1)
    blue = np.random.rand(len(unique_lang) + 1)

    for l in unique_lang:
        q = "original_language == " + "'" + l + "'"
        val = df13.query(q)
        if first:
            ax = val.plot.scatter(x='vote_average', y='success_impact', c=np.array(
                [red[color], green[color], blue[color]]), figsize=(10, 10))
            first = False
            color = color + 1
        ax = val.plot.scatter(x='vote_average', y='success_impact', ax=ax, c=np.array(
            [red[color], green[color], blue[color]]), figsize=(10, 10))
        color = color + 1
    plt.legend(unique_lang, loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.title("vote_average vs impact_success")
    plt.tight_layout()

    #################################################

    plt.savefig("{}-Q13.png".format(studentid))
    plt.clf()


if __name__ == "__main__":
    df1 = question_1("movies.csv", "credits.csv")   # done
    df2 = question_2(df1)       # done
    df3 = question_3(df2)       # done
    df4 = question_4(df3)       # done
    df5 = question_5(df4)       # done
    df6 = question_6(df5)       # done
    df7 = question_7(df6)       # done
    df8 = question_8(df7)       # done
    movies = question_9(df8)    # done
    df10 = question_10(df8)     # done
    question_11(df10)           # done
    question_12(df10)           # done
    question_13(df10)           # done
