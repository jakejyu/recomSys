
__author__ = 'Jiang'

# Project: recommendation system for event-based on line social networking.
# Data from meetup.com:

# part 1: recommend new events to users
# - Algorithm 1 ranking according to event similarity (event description)

from collections import OrderedDict

import sys
import json
import nltk
import re  # regular expression
import pprint  # to implement Vividict - nested dictionaries

"""
Incremental developing steps:
 -Extract all the text from .json files
 -Extract event description
 -Extract tokens of description
 -Build the whole entity diction for all events in a group and nested dictionaries for each event.
  (remove duplicates, words whose length < 2 and stopwords)
 -Compute the cosine similarity for event pairs
 -Build the [year, 'name rank', ... ] list
 -Fix main() to use the extract_names list
 -
"""


class Vividict(dict):
    """
    implement nested dictionaries
    e.g. of usage
    d = Vividict()
    d['foo']['bar']
    d['foo']['baz']
    d['fizz']['buzz']
    d['primary']['secondary']['tertiary']['quaternary']
    pprint.pprint(d)
    Which outputs:
    {'fizz': {'buzz': {}},
     'foo': {'bar': {}, 'baz': {}},
     'primary': {'secondary': {'tertiary': {'quaternary': {}}}}}

     refer to
    http://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python/19829714#19829714
    """

    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


def get_entity_dictionary(filename):
    """ Input: a .json file name and the stopwords file name
    Return: the entity Dictionary of all descriptions of all events; the entity Dictionary for each event"""
    # load event data json file
    try:
        json_data = open(filename)
        event_data = json.load(json_data)
        json_data.close()
    except IOError:
        print('IO Error in reading file:', filename)
    # read stopwords file
    try:
        f = open("stop_words.txt")
        stopwords = f.read()
        f.close()
    except IOError:
        print('IO Error reading file: stopwords.txt')
    # build entity dictionaries for all events' description and each one/'s
    dic = {}  # the whole dic
    dic_event = Vividict()  # nested dic for all events
    count_event = 0  # count the total number of events in the group
    for item in event_data:
        try:
            description_event = item["description"]
            event_id = item["id"]
            # use the time of event as the first layer key for dic_event dictionary
            # time_event = item["time"]
            count_event += 1
            # parse description in each event
            tokens = nltk.word_tokenize(description_event)
            for token in tokens:
                # use regular expression to choose words starting with a word character
                match = re.search(r'\w+', token)
                if match:
                    # remove stopwords and tokens of length<2, change token to lower case
                    word = token.lower()
                    if word not in stopwords and len(word) > 2:
                        if word in dic:
                            dic[word] += 1
                        else:
                            dic[word] = 1
                        if word in dic_event[event_id]:
                            dic_event[event_id][word] += 1
                        else:
                            dic_event[event_id][word] = 1
        except:
            continue
        # print ('ERROR in parsing description!')
    return dic, dic_event, count_event


def compute_cosine_similarity(dic1, dic2):
    """
    Input: two dictionaries
    Return: cosine similarity of them
    similarity: cosine theta = (L*K)/(|L|*|K|)
    """
    count = 0
    for item in dic1:
        try:
            if item in dic2:
                count += 1
            # print (item) # for debugging
        except:
            print('Error in computing similarity!')
    similarity = count / (len(dic1) * len(dic2)) ** 0.5
    # print (count, len(dic1), len(dic2)) # for debugging
    return similarity


def similarity_cosine_re(dic1, dic2):
    """
    Input: two dictionaries
    Return: revised cosine similarity of them taking the times of appearance of entity words in event desription
    similarity: cosine theta = (L*K)/(|L|*|K|)
    """
    count = 0
    for key in dic1:
        try:
            if key in dic2:
                count += min(dic1[key], dic2[key])
            # print (key) # for debugging
        except:
            print('Error in computing revised similarity!')
    similarity = count / (sum(dic1.values()) * sum(dic2.values())) ** 0.5
    # print (count, len(dic1), len(dic2)) # for debugging
    return similarity


def split_events(dic_event):
    """
    Input: nested entity dictionary of events
    Return: two nested dics for known events and unknown events
    """
    dic_known = {}
    dic_unknown = {}
    try:
        for key in dic_event:
            # print ('key:', key)# for debugging
            # regular expression: ^ force to match the begining of the string
            # use events after 2014 year as unknow events for recommendation
            match = re.search(r'^14\w+', str(key))  # need to convert key into string!
            if match:
                dic_unknown[key] = dic_event[key]
            else:
                dic_known[key] = dic_event[key]
    except:
        print('Error in split Events!')
    return dic_known, dic_unknown


def get_recommended_users(sorted_future_past_event_simi_table, group_id, max_num_recommend_events):
    # read groupEventMember file
    try:
        f = open('E:/projects/data/groupEventMember/' + group_id + '.txt')
        group_event_member = f.read().splitlines()
        f.close()
    except IOError:
        print('IO Error reading file: groupEventMember')
    # read groupEventMember file
    try:
        f = open('E:/projects/data/groupEventMemberSequence/' + group_id + '.txt')
        group_event_member_sequence = f.read().split()
        f.close()
    except IOError:
        print('IO Error reading file: groupEventMemberSequence')

    # with open('output/test_group_event_member_sequence' + group_id + '.txt', 'w') as outfile:
    #     json.dump(group_event_member_sequence, outfile)
    # with open('output/test_group_event_member' + group_id + '.txt', 'w') as outfile:
    #     json.dump(group_event_member, outfile)

    # get recommended users for the future events in the group
    recommended_users = {}
    for key_future_event in sorted_future_past_event_simi_table:
        num_recommend_users = 0
        for key in sorted_future_past_event_simi_table[key_future_event]:

            event_index = int(group_event_member_sequence.index(key) / 2)  # get the index of the similar event.
            # need to divided by 2, because the date entries double the size.
            # print(key, event_index)
            # print(group_event_member[event_index])
            user_index_line = group_event_member[event_index].split()  # split into user index
            # print(user_index_line)

            recommend_user_index = 0
            # print("Recommended users are: ")
            for user_attend_indicate in user_index_line:
                if num_recommend_users > max_num_recommend_events:
                    break
                if user_attend_indicate == "1":
                    # print(user_index_line.index(user))
                    # print(str(recommend_user_index))
                    if recommended_users.__contains__(key_future_event):
                        if recommend_user_index not in recommended_users[key_future_event]:
                            num_recommend_users += 1
                            recommended_users[key_future_event].add(recommend_user_index)
                    else:
                        recommended_users[key_future_event] = {recommend_user_index}
                        num_recommend_users += 1
                    # print(user_index_line.__sizeof__())
                recommend_user_index += 1

    # with open('output/recommended_users' + group_id + '.txt', 'w') as outfile:
    # json.dump(recommended_users, outfile)

    return recommended_users

#  Turn sets into lists before serializing, or use a custom default handler to do so:
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def main():
    """
    call functions to compute similarity and rank them
    Output: recommended users for events in a group
    """

    while len(sys.argv) != 3 or int(sys.argv[2]) <= 0:
        print('Wrong input!')
        print('Please input a group ID and top K recommending users again!')
        sys.exit(1)
        # try:
        #     group_id = sys.argv[1]
        #     max_num_recommend_events = int(sys.argv[2]) - 1  # max num of events recommending for each user,
        #     break
        # except ValueError:
        #     print("Oops!  That was no valid input.  Try again...")
        #     print('Usage: Please input a group ID and top K recommending users!')

    # if not sys.argv or len(sys.argv) != 3 or sys.argv[2] <= 0:
    #     print('Wrong input! Please input a group ID and top K recommending users!')
    #     sys.exit(1)

    group_id = sys.argv[1]
    max_num_recommend_events = int(sys.argv[2]) - 1  # max num of events recommending for each user,
    # maybe less due to fewer events of insufficient similar users

    try:
        (dic, dic_event, count_event) = get_entity_dictionary('E:/projects/data/Meetup/events/' + group_id + '.json')
    except:
        print('Error in get_dictionary!')
        print('Please input a group ID and top K recommending users again!')
        sys.exit(1)

    (dic_known, dic_unknown) = split_events(dic_event)

    similarity_re = {}
    for keyUnknown in dic_unknown:
        similarity_re[keyUnknown] = {}
        for keyKnown in dic_known:
            similarity_re[keyUnknown][keyKnown] = similarity_cosine_re(dic_unknown[keyUnknown], dic_known[keyKnown])
            # similarity_re[(keyUnknown, keyKnown)] = similarity_cosine_re(dic_unknown[keyUnknown], dic_known[keyKnown])
        # print (similarity_re)

    # file_similar = open('output/similarity' + group_id + '.txt', 'w')
    # # file_similar.write('Ranked similarity:\n')
    # # ??? how to sorted by key[1] and key=similarity_re.get, sort twice???
    # for key in similarity_re:
    # # for key in sorted(similarity_re, key=similarity_re.get, reverse=True):
    # #     similarity_ranked_re[key] = similarity_re[key]
    #     # print (similarity_ranked_re[key])
    #     file_similar.write(str(key))
    #     file_similar.write(str(similarity_re[key]) + '\n')
    #     # if similarity_ranked_re[key] == 1:  # for debugging
    #     #     file_similar.write(str(sorted(dic_event[key[0]])) + '\n')  # for debugging
    #     #     file_similar.write(str(sorted(dic_event[key[1]])) + '\n')  # for debugging
    # file_similar.close()

    future_past_event_simi_table = {}
    for key in similarity_re:
        future_past_event_simi_table_tmp = {}
        for key_temp in similarity_re[key]:
            similarity_tmp = similarity_re[key][key_temp]
            future_past_event_simi_table_tmp[key_temp] = similarity_tmp
            if similarity_tmp > 0:  # if similarity > 0, will potentially recommend it's users
                if future_past_event_simi_table.__contains__(key):
                    future_past_event_simi_table[key].update(future_past_event_simi_table_tmp)
                else:
                    future_past_event_simi_table[key] = future_past_event_simi_table_tmp

    # print("Recommended user past events are" + str(future_past_event_simi_table))

    # sort the dic
    sorted_future_past_event_simi_table = {}
    for key in future_past_event_simi_table:
        tmp = future_past_event_simi_table[key]
        sorted_list = sorted(tmp.items(), key=lambda x: x[1], reverse=True)
        ord_dic = OrderedDict(sorted_list)
        sorted_future_past_event_simi_table[key] = ord_dic


    with open('output/intermediate_data/sorted_future_past_event_simi_table' + group_id + '.txt', 'w') as outfile:
        json.dump(sorted_future_past_event_simi_table, outfile)

    # for key in future_past_event_simi_table:
    #     print(key)
    #     for i, val in enumerate(future_past_event_simi_table[key]):
    #     # for key_temp in future_past_event_simi_table[key]:
    #         print(i, val)


    recommended_users = get_recommended_users(sorted_future_past_event_simi_table, group_id, max_num_recommend_events)

    with open('output/recommended_users_for_events_in_group_' + group_id + '.txt', 'w') as outfile:
        json.dump(recommended_users, outfile, default=set_default)

    # file_recom = open('output/' + group_id + '.txt', 'w')
    # file_recom.write("Recommended users for the the event " + " are :")
    # file_recom.close()

    # print (dic)
    #    print (dic_event)

    # print out recommendation results
    print("Recommend users for new event, based on event similarity!")
    print("The Top " + str(max_num_recommend_events + 1) + " recommendation result for group " + group_id +
          " is as follows!")
    for key in recommended_users:
        print("The user Id of recommended users for the event " + key + " are: ")
        print(recommended_users[key])

    # print('The total number of events in the group is:', count_event)

# print ('Revised Similarity is:', similarity_re)
#    print ('Ranked Revised Similarity is:', similarity_ranked_re)
#    print ('Recommend users are:?')

if __name__ == '__main__':
    main()
