__author__ = 'Jiang'

# - cluster users into a few groups based on user similarity (event attendance history)
# - more features such as user profiles could be added

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
    # input group id
    args = sys.argv[1]
    while not args:
        print('usage: please input a group ID!')

    group_id = sys.argv[1]

    max_num_recommend_events = int(sys.argv[2])-1  # max num of events recommending for each user,
    # maybe less due to fewer events of insufficient similar users

    # read groupEventMember file
    try:
        f = open('E:/projects/data/groupEventMember/' + group_id + '.txt')
        group_event_member = f.read().splitlines()
        # group_event_member = [map(int, line.split(' ')) for line in f]
        f.close()
    except IOError:
        print('IO Error reading file: groupEventMember')

    event_user_matrix = []
    with open('E:/projects/data/groupEventMember/' + group_id + '.txt') as f:  # a with block will auto close your file after the statements within it
        # w, h = [int(x) for x in f.readline().split()] # read first line
        for line in f:
            # line = line.strip()  # strip off any trailing whitespace(including '\n')
            event_user_matrix.append([int(x) for x in line.split()])

    with open('output/event_user_matrix' + group_id + '.txt', 'w') as outfile:
        json.dump(event_user_matrix, outfile)

    row_num = len(event_user_matrix)
    colum_num = len(event_user_matrix[0])
    # print(row_num)
    # print(colum_num)

    # print(event_user_matrix[0][0])
    # print(event_user_matrix[405][506])

    event_attended_simi_table = {}
    for j in range(0, colum_num):
        # past_evets_self =
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
                    # print(self_num, other_num, both_num)
                    cos_similarity = both_num/(self_num**(1.0/2.0) * other_num**(1.0/2.0))
                    event_attended_simi_table_tmp[k] = cos_similarity
                    if j not in event_attended_simi_table:
                        event_attended_simi_table[j] = event_attended_simi_table_tmp
                    else:
                        event_attended_simi_table[j].update(event_attended_simi_table_tmp)
                    # if cos_similarity != 0:
                    #     print(j, k, self_num, other_num, both_num, cos_similarity)
                else:
                    event_attended_simi_table_tmp[k] = 0
                    if j not in event_attended_simi_table:
                        event_attended_simi_table[j] = event_attended_simi_table_tmp
                    else:
                        event_attended_simi_table[j].update(event_attended_simi_table_tmp)
                    # event_attended_simi_table[j][k] = 0
                # if event_attended_simi_table.__contains__(j):
                #     event_attended_simi_table[j][k].append(similarity_tmp)
                # else:
                #     event_attended_simi_table[j][k] = [similarity_tmp]

    with open('output/event_attended_simi_table' + group_id + '.txt', 'w') as outfile:
            json.dump(event_attended_simi_table, outfile)

    # compute similar users for each user in the group
    user_cluster = {}
    for key in event_attended_simi_table:
        # user_cluster_temp = {}
        tmp = event_attended_simi_table[key]
        sorted_list = sorted(tmp.items(), key=lambda x: x[1], reverse=True)
        ord_dic = OrderedDict(sorted_list)
        for key_ord in ord_dic:
            if ord_dic[key_ord] > 0.2:  # group users with similarity of 0.2 into one group
                if user_cluster.__contains__(key):
                    # user_cluster[key].append([key_ord, ord_dic[key_ord]])
                    user_cluster[key].append(key_ord)
                else:
                    # user_cluster[key] = [key_ord, ord_dic[key_ord]]
                    user_cluster[key] = [key_ord]


        # for key_tmp in tmp:
        #     tmp_sorted = sorted(tmp.items(), key=lambda tmp: tmp[1])
    # sorted(your_list, key=lambda x: (your_dict[x]['downloads'], your_dict[x]['date']))

        # with open('output/tmp_sorted' + group_id + '.txt', 'w') as outfile:
        #         json.dump(tmp, outfile)

    with open('output/user_cluster' + group_id + '.txt', 'w') as outfile:
            json.dump(user_cluster, outfile)


    # # get recommended events for each users in the group
    # recom_events_dic = {}
    # for user in recom_users_dic:
    #     num_recommend_event = 0
    #     # print(recom_users_dic[user])
    #     # print(user)
    #     tmp_list = recom_users_dic[user]
    #     for val in tmp_list:  # get the events the "val" attend but the "user" do not
    #         if num_recommend_event > max_num_recommend_events:
    #             break
    #         for i in range(0, row_num):
    #             if event_user_matrix[i][val] == 1 and event_user_matrix[i][user] == 0:
    #                 if recom_events_dic.__contains__(user):
    #                     if i not in recom_events_dic[user]:
    #                         num_recommend_event += 1
    #                         recom_events_dic[user].add(i)
    #                 else:
    #                     recom_events_dic[user] = {i}  # add event i
    #                     num_recommend_event += 1
    #             if num_recommend_event > max_num_recommend_events:
    #                 break
    #
    # with open('output/recom_events_for_users_in_group_' + group_id + '.txt', 'w') as outfile:
    #         json.dump(recom_events_dic, outfile, default=set_default)


if __name__ == '__main__':
    main()
