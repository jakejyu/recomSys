
__author__ = 'Jiang'

# Project: recommendation system for event-based on line social networking.
# 2015-05-03
# Data from meetup.com

# part 2: recommend new events to users
# - Ranking according to user similarity (event attendance history matrix)

import sys
import json

from collections import OrderedDict


#  Turn sets into lists before serializing, or use a custom default handler to do so:
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def main():
    """
    Input: group ID
    Output: recommended events for some users in the group
    """
    # input group id and number of recommend results
    while len(sys.argv) != 3 or int(sys.argv[2]) <= 0:
        print('Wrong input!')
        print('Please input a group ID and top K recommending users again!')
        sys.exit(1)

    group_id = sys.argv[1]
    max_num_recommend_events = int(sys.argv[2])-1  # max num of events recommending for each user,
    # maybe less due to fewer events of insufficient similar users

    # read groupEventMember file
    try:
        f = open('E:/projects/data/groupEventMember/' + group_id + '.txt')
        group_event_member = f.read().splitlines()
        f.close()
    except IOError:
        print('IO Error reading file: groupEventMember')
        print('Please input a group ID and top K recommending users again!')
        sys.exit(1)

    event_user_matrix = []
    with open('E:/projects/data/groupEventMember/' + group_id + '.txt') as f:  # a with block will auto close your file
    #  after the statements within it
        for line in f:
            # line = line.strip()  # strip off any trailing whitespace(including '\n')
            event_user_matrix.append([int(x) for x in line.split()])

    with open('output/intermediate_data/event_user_matrix' + group_id + '.txt', 'w') as outfile:
        json.dump(event_user_matrix, outfile)

    row_num = len(event_user_matrix)
    colum_num = len(event_user_matrix[0])

    event_attended_simi_table = {}
    for j in range(0, colum_num):
        for k in range(0, colum_num):
            if j != k:
                event_attended_simi_table_tmp = {}
                self_num = 0
                other_num = 0
                both_num = 0
                for i in range(0, row_num):
                    if event_user_matrix[i][j] == 1:
                        self_num += 1
                        if event_user_matrix[i][j] == event_user_matrix[i][k]:
                            both_num += 1
                    if event_user_matrix[i][k] == 1:
                        other_num += 1
                if self_num != 0 and other_num != 0:
                    cos_similarity = both_num/(self_num**(1.0/2.0) * other_num**(1.0/2.0))
                    event_attended_simi_table_tmp[k] = cos_similarity
                    if j not in event_attended_simi_table:
                        event_attended_simi_table[j] = event_attended_simi_table_tmp
                    else:
                        event_attended_simi_table[j].update(event_attended_simi_table_tmp)
                else:
                    event_attended_simi_table_tmp[k] = 0
                    if j not in event_attended_simi_table:
                        event_attended_simi_table[j] = event_attended_simi_table_tmp
                    else:
                        event_attended_simi_table[j].update(event_attended_simi_table_tmp)

    with open('output/intermediate_data/event_attended_simi_table' + group_id + '.txt', 'w') as outfile:
            json.dump(event_attended_simi_table, outfile)

    # compute similar users for each user in the group
    recom_users_dic = {}
    for key in event_attended_simi_table:
        tmp = event_attended_simi_table[key]
        sorted_list = sorted(tmp.items(), key=lambda x: x[1], reverse=True)
        ord_dic = OrderedDict(sorted_list)
        for key_ord in ord_dic:
            if ord_dic[key_ord] > 0:
                if recom_users_dic.__contains__(key):
                    # recom_users_dic[key].append([key_ord, ord_dic[key_ord]])
                    recom_users_dic[key].append(key_ord)
                else:
                    # recom_users_dic[key] = [key_ord, ord_dic[key_ord]]
                    recom_users_dic[key] = [key_ord]

    with open('output/intermediate_data/recom_users_dic' + group_id + '.txt', 'w') as outfile:
            json.dump(recom_users_dic, outfile)

    # get recommended events for each users in the group
    recom_events_dic = {}
    for user in recom_users_dic:
        num_recommend_event = 0
        tmp_list = recom_users_dic[user]
        # get the events the "val" attend but the "user" do not
        for val in tmp_list:
            if num_recommend_event > max_num_recommend_events:
                break
            for i in range(0, row_num):
                if event_user_matrix[i][val] == 1 and event_user_matrix[i][user] == 0:
                    if recom_events_dic.__contains__(user):
                        if i not in recom_events_dic[user]:
                            num_recommend_event += 1
                            recom_events_dic[user].add(i)
                    else:
                        recom_events_dic[user] = {i}  # add event i
                        num_recommend_event += 1
                if num_recommend_event > max_num_recommend_events:
                    break

    with open('output/recommended_events_for_users_in_group_' + group_id + '.txt', 'w') as outfile:
            json.dump(recom_events_dic, outfile, default=set_default)

    # print out recommendation results
    print("Recommend events for all users in the group, based on user past attendance history!")
    print("The Top " + str(max_num_recommend_events + 1) + " recommendation result for group " + group_id +
          " is as follows!")
    for key in recom_events_dic:
        print("The event Id of recommended events for the user " + str(key) + " are: ")
        print(recom_events_dic[key])

if __name__ == '__main__':
    main()
