import datetime
import os
import random
import collections
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite


def time_std(times):
    print('To calculate the var.')
    # to transform to numbers
    numbers = []
    for t in times:
        year = t[:4]
        month = t[5:7]
        day = t[8:10]
        dt = datetime.datetime(int(year), int(month), int(day))
        t1970 = datetime.datetime(1970, 1, 1)
        numbers.append((dt - t1970).days)
    return np.std(numbers)


def time_error(times, log):
    # time like 2020-08-12 20:31
    log.write(f'#####Calculate time error of {times}.\n')
    # print(f'Calculate time error of {times}')
    time_differences = []
    means = []
    error_var = 0
    for index_1, time_1 in enumerate(times):
        time_difference = []
        for index_2, time_2 in enumerate(times):
            if index_1 == index_2:
                continue
            # compute the time difference
            # first translate 2020年04月07日 18:53 to 2020-04-07 18:53:00
            year = time_1[:4]
            month = time_1[5:7]
            day = time_1[8:10]
            dt_1 = datetime.datetime(int(year), int(month), int(day))

            year = time_2[:4]
            month = time_2[5:7]
            day = time_2[8:10]
            dt_2 = datetime.datetime(int(year), int(month), int(day))

            time_diff = abs((dt_1 - dt_2).days)
            log.write(f'-----Time error between {time_1} and {time_2} is: {time_diff} days.\n')
            time_difference.append(time_diff)

        mean_time_diff = np.mean(time_difference)
        means.append(mean_time_diff)
        for diff in time_difference:
            error_var += (diff - mean_time_diff) * (diff - mean_time_diff)

        time_differences.append(error_var)

    # return time_differences
    avg = np.mean(time_differences)
    min = np.min(time_differences)
    # avg = np.min(means)  # or mean
    # log.write(f'Time errors: {means}, and we pick {avg}\n')
    # print(f'mean of time error: {avg}')
    return avg
    # return min


def close_or_not(time_1, time_2):
    # first translate 2020年04月07日 18:53 to 2020-04-07 18:53:00
    year1 = time_1[:4]
    month1 = time_1[5:7]
    day1 = time_1[8:10]
    hour1 = time_1[11:13]
    minute1 = time_1[14:16]
    dt_1 = datetime.datetime(int(year1), int(month1), int(day1))

    year2 = time_2[:4]
    month2 = time_2[5:7]
    day2 = time_2[8:10]
    hour2 = time_2[11:13]
    minute2 = time_2[14:16]
    dt_2 = datetime.datetime(int(year2), int(month2), int(day2))

    day_diff = abs((dt_1 - dt_2).days)

    hour_diff = abs(int(hour1) - int(hour2))
    minute_diff = abs(int(minute1) - int(minute2))
    if day_diff == 0 and hour_diff == 0:
        return True
    else:
        return False


def get_random():
    random.seed()
    return random.random()


# to extend from inside to outside
def get_distance(inside, outside):  # format: [user, content, time]
    if inside[0] == outside[0]:  # user
        return True
    if inside[1] == outside[1]:  # content; or scare scenario oriented, referring to dt2.py
        return True
    if close_or_not(inside[2], outside[2]):  # time
        return True

    return False


if __name__ == '__main__':
    review_nodes = dict()
    # review_index = 0
    sprite_nodes = dict()
    # sprite_index = 0
    all_reviewers = dict()
    all_sprites = dict()
    id_user = dict()
    rs_edges = []
    ss_edges = []
    seeds = []
    th1 = 3
    th2 = 10
    th3 = 3
    th4 = 3
    reviewer_spammers = []  # name
    follower_spammers = []  # name

    log_path = 'log_on_graph.txt'
    log_file = open(log_path, 'w', encoding='utf-8')
    result_path = 'result_on_graph_across_brands.txt'

    # to collect all reviewers so as to find duplicated posts
    for cf in os.listdir('.'):
        if '_comments.csv' not in cf:
            continue
        reviews = pd.read_csv(cf, encoding='ansi')
        # format: id,guid,name,time,score,content,praise,reply
        for index, row in reviews.iterrows():
            reviewer = row['name']
            if reviewer not in all_reviewers.keys():
                all_reviewers[reviewer] = 1
            else:
                all_reviewers[reviewer] += 1

    for sf in os.listdir('.'):
        if '_sprites_verbose.csv' in sf:
            reviews = pd.read_csv(sf)
            # append the last line
            # last_row = pd.DataFrame([None, None, None, None, None, None, None, None],
            #                         columns=['guid', 'reviewer', 'r_content', 'r_time', 'reply', 'cid', 'rid',
            #                         "follower", "f_content", 'f_time'])
            # reviews.append(last_row, ignore_index=True)
            followers = []
            old_cid = ''
            # format: guid,reviewer,r_content,r_time,reply,cid,rid,follower,f_content,f_time
            for index, row in reviews.iterrows():
                name = row['reviewer']
                follower = row['follower']
                r_time = row['r_time']
                r_content = row['r_content']
                reply = row['reply']
                f_content = row['f_content']
                f_time = row['f_time']
                cid = row['cid']
                rid = row['rid']

                if cid not in id_user.keys():
                    id_user[cid] = name
                else:
                    log_file.write(f'!!!!! Duplicate cid!!! {cid, name}\n')
                if rid not in id_user.keys():
                    id_user[rid] = follower
                else:
                    log_file.write(f'!!!!! Duplicate rid!!! {rid, follower}\n')

                if follower not in all_sprites.keys():
                    all_sprites[follower] = 1
                else:
                    all_sprites[follower] += 1

                if rid in sprite_nodes.keys():
                    # If there are duplicates, append a suffix
                    rid = str(rid) + '%%%' + str(get_random())
                    log_file.write(f'ALERT! Duplicate follower names encountered! {rid, follower}\n')
                sprite_nodes[rid] = [follower, f_content, f_time]

                # still the same review and its sprites
                if cid == old_cid or '%%%' in str(old_cid) and str(cid) == old_cid.split('%%%')[0]:
                    rs_edges.append((old_cid, rid))

                else:
                    # new reviewer found
                    if cid in review_nodes.keys():
                        # If there are duplicates, append a suffix
                        cid = str(cid) + '%%%' + str(get_random())
                        log_file.write(f'ALERT! Duplicate reviewer names encountered! {cid, name}\n')
                    review_nodes[cid] = [name, r_content, r_time]
                    rs_edges.append((cid, rid))
                    # to link all followers affiliated to the same review together
                    if len(followers) > 1:
                        for i1, f1 in enumerate(followers):
                            for i2, f2 in enumerate(followers):
                                if i1 == i2:
                                    continue
                                ss_edges.append((f1, f2))
                        old_cid = cid
                        followers = []
                followers.append(rid)  # prepare for ss_edges

                # u receives too many comments (more than the threshold θ_2),
                if reply > th2:
                    reviewer_spammers.append(reviewer)

                # or t is too close to its review (〖<θ〗_b)
                if close_or_not(r_time, f_time):
                    follower_spammers.append(follower)

            # last reviewer and its followers to address
            if len(followers) > 1:
                for i1, f1 in enumerate(followers):
                    for i2, f2 in enumerate(followers):
                        if i1 == i2:
                            continue
                        ss_edges.append((f1, f2))

    print(f'Count of review_nodes: {len(review_nodes.keys())}')
    print(f'Count of sprite_nodes:: {len(sprite_nodes.keys())}')
    print(f'Count of rs_edges: {len(rs_edges)}')
    print(f'Count of ss_edges: {len(ss_edges)}')

    # construct a brand graph
    B = nx.Graph()
    B.add_nodes_from(review_nodes.keys(), bipartite=0)  # format: user: [content, time]
    B.add_nodes_from(sprite_nodes.keys(), bipartite=1)  # format: user: [content, time]

    # to find any followers that are also reviewers
    reviewers_also_followers = []
    for reviewer in review_nodes.keys():
        if reviewer in sprite_nodes.keys():
            reviewers_also_followers.append(reviewer)

    log_file.write(f'reviewers_also_followers: {len(reviewers_also_followers)}: {reviewers_also_followers}\n')

    # to start calculate spammer post duplicates
    # or using %%% in cid/rid to match
    neat_reviewers = []
    for review, detail in review_nodes.items():
        reviewer = detail[0]
        neat_reviewers.append(reviewer)

    neat_reviewers = list(set(neat_reviewers))
    neat_ratio_of_reviewers = len(neat_reviewers) / len(review_nodes.keys())

    # for follower
    neat_followers = []
    for follow, detail in sprite_nodes.items():
        follower = detail[0]
        neat_followers.append(follower)

    neat_followers = list(set(neat_followers))
    neat_ratio_of_followers = len(neat_followers) / len(sprite_nodes.keys())

    print(f'ratio of duplicate in multi-posting of reviewers: {1 - neat_ratio_of_reviewers}')
    print(f'ratio of duplicate in multi-following of followers: {1 - neat_ratio_of_followers}')

    # to start with some spam seeds
    # if u posts too many times (more than the threshold θ_1),

    # or c duplicates with another review
    for c1, data1 in review_nodes.items():  # cid: name, content, time
        for c2, data2 in review_nodes.items():
            if c1 == c2:
                continue
            if data1[1] == data2[1]:
                if '%%%' in str(c1):
                    reviewer_spammers.append(id_user[int(c1.split(r'%%%')[0])])
                else:
                    reviewer_spammers.append(id_user[c1])

                if '%%%' in str(c2):
                    reviewer_spammers.append(id_user[int(c2.split(r'%%%')[0])])
                else:
                    reviewer_spammers.append(id_user[c2])

    # !!! or t falls into a narrow time window of review burstiness; Need to be done around one item/brand
    # first cluster these posting times into clusters based on k-means or other
    # and then check if t is within a larger cluster.


    # Definition 2: Given a comment y (u, c, t); if u responses too many times (〖>θ〗_a),
    for follower, count in all_sprites.items():
        if count > th1:
            follower_spammers.append(follower)

    # or c duplicates with another comment or review,
    for r1, data1 in sprite_nodes.items():  # rid: name, content, time
        for r2, data2 in sprite_nodes.items():
            if r1 == r2:
                continue
            if data1[1] == data2[1]:
                if '%%%' in str(r1):
                    follower_spammers.append(id_user[int(r1.split(r'%%%')[0])])
                else:
                    follower_spammers.append(id_user[r1])

                if '%%%' in str(r2):
                    follower_spammers.append(id_user[int(r2.split(r'%%%')[0])])
                else:
                    follower_spammers.append(id_user[r2])

    # or t falls into a narrow time window (〖<θ〗_b) of comment burstiness

    # Definition 3: When customer u affiliates to a first-class review x and a comment y in G
    reviewers_also_followers = []
    for c, data_c in review_nodes.items():  # cid: name, content, time
        for r, data_r in sprite_nodes.items():  # rid: name, content, time
            if data_c[0] == data_r[0]:
                reviewers_also_followers.append(data_c[0])
    for user in reviewers_also_followers:
        reviewer_spammers.append(user)
        follower_spammers.append(user)
    # Definition 4: if the reviewer-commenter pair (u1, u2) appears abnormally too many times (>θ) in G,
    rs_edge_count = collections.Counter(rs_edges)
    for rs, count in rs_edge_count.items():
        if count > th1:
            reviewer_spammers.append(rs[0])
            follower_spammers.append(rs[1])
    # or its inverse (u2, u1) is also applicable in the dataset, both x and y are spam seeds.
    # Done in previous steps

    # to calculate spammer count
    reviewer_spammers = list(set(reviewer_spammers))
    follower_spammers = list(set(follower_spammers))
    print(f'Ratio of reviewer spammer seeds: {len(reviewer_spammers) / len(neat_reviewers)}')
    print(f'Ratio of follower spammer seeds: {len(follower_spammers) / len(neat_followers)}')

    # --> Start propagating
    # propagate to absorb one, if the distance is acceptable
    # start iterating
    round = 1000
    ss_extended = 0
    for i in range(round):
        extended = 0
        for rs in rs_edges:
            cid = rs[0]  # cid
            # KeyError: '12346404883%%%0.6903497627398195'
            if '%%%' in str(cid):
                reviewer = id_user[int(cid.split(r'%%%')[0])]
            else:
                reviewer = id_user[cid]
            rid = rs[1]  # rid
            if '%%%' in str(rid):
                follower = id_user[int(rid.split(r'%%%')[0])]
            else:
                follower = id_user[rid]
            if reviewer in reviewer_spammers and follower not in follower_spammers:  # reviewer --> follower
                if get_distance(review_nodes[cid], sprite_nodes[rid]):
                    log_file.write(f'From rs --> extend a follower: {follower}\n')
                    extended += 1
                    follower_spammers.append(follower)
            elif reviewer not in reviewer_spammers and follower in follower_spammers:  # follower --> reviewer
                if get_distance(sprite_nodes[rid], review_nodes[cid]):
                    log_file.write(f'From rs --> extend a reviewer: {reviewer}\n')
                    extended += 1
                    reviewer_spammers.append(reviewer)

        for ss in ss_edges:
            rid1 = rs[0]
            if '%%%' in str(rid1):
                f1 = id_user[int(rid1.split(r'%%%')[0])]
            else:
                f1 = id_user[rid1]
            rid2 = rs[1]
            if '%%%' in str(rid2):
                f1 = id_user[int(rid2.split(r'%%%')[0])]
            else:
                f2 = id_user[rid2]
            if f1 in follower_spammers and f2 not in follower_spammers:
                if get_distance(sprite_nodes[rid1], sprite_nodes[rid2]):
                    log_file.write(f'From ss --> extend a follower: {f2}\n')
                    extended += 1
                    ss_extended += 1
                    follower_spammers.append(f2)
            elif f2 in follower_spammers and f1 not in follower_spammers:
                if get_distance(sprite_nodes[rid2], sprite_nodes[rid1]):
                    log_file.write(f'From ss --> extend a follower: {f1}\n')
                    extended += 1
                    ss_extended += 1
                    follower_spammers.append(f1)
        if extended == 0:
            break

    reviewer_spammers = list(set(reviewer_spammers))
    follower_spammers = list(set(follower_spammers))

    print('To verify something with these containers.\n')
    r_contents = []
    r_times = []
    for reviewer in reviewer_spammers:
        for cid, data in review_nodes.items():
            if data[0] == reviewer:
                r_contents.append(data[1])
                r_times.append(data[2])
    # time_error_of_spammed_reviews = time_error(r_times, log_file)
    time_error_of_spammed_reviews = time_std(r_times)
    r_contents_set = list(set(r_contents))
    duplication_level_of_spammed_reviews = 1 - len(r_contents_set)/len(r_contents)

    f_contents = []
    f_times = []
    for follower in follower_spammers:
        for rid, data in sprite_nodes.items():
            if data[0] == follower:
                f_contents.append(data[1])
                f_times.append(data[2])
    # time_error_of_spammed_sprites = time_error(f_times, log_file)
    time_error_of_spammed_sprites = time_std(f_times)
    f_contents_set = list(set(f_contents))
    duplication_level_of_spammed_sprites = 1 - len(f_contents_set) / len(f_contents)

    print(f'Ratio of reviewer spammers: {len(reviewer_spammers) / len(neat_reviewers)}')
    print(f'Ratio of follower spammers: {len(follower_spammers) / len(neat_followers)}')
    print(f'Total follower-->follower spamming propagation count: {ss_extended}')
    print(f'Ratio of duplicated contents within spammed reviews: {duplication_level_of_spammed_reviews}')
    print(f'Ratio of duplicated contents within spammed sprites: {duplication_level_of_spammed_sprites}')
    print(f'Time error of duplicated contents within spammed reviews: {time_error_of_spammed_reviews}')
    print(f'Time error of duplicated contents within spammed sprites: {time_error_of_spammed_sprites}')

    with open(result_path, 'w', encoding='utf-8') as rf:
        rf.write(f'reviewer_nodes: {str(review_nodes)}\n')
        rf.write(f'follower_nodes: {str(sprite_nodes)}\n')
        rf.write(f'rs_edges: {str(rs_edges)}\n')
        rf.write(f'ss_edges:{str(ss_edges)}\n')
        rf.write(f'reviewer_spammers: {str(reviewer_spammers)}\n')
        rf.write(f'follower_spammers: {str(follower_spammers)}\n')

    # write follower details into csv file

    # prepare to write into gephi
    # format of nodes:
    # Source,Target,Type,Weight
    # 1,3,Directed,5
    # format of edges:
    # Source, Target, Type, Weight
    # 1, 2, Directed, 10

    # Add edges to graph B
    # Apply edge weight to represent spammers
    edges = []
    spam_edges = []
    benign_edges = []
    for edge in rs_edges:
        cid = edge[0]
        rid = edge[1]
        if '%%%' in str(cid):
            cid = int(cid.split('%%%')[0])
        if '%%%' in str(rid):
            rid = int(rid.split('%%%')[0])
        if id_user[cid] in reviewer_spammers and id_user[rid] in follower_spammers:
            spam_edges.append([cid, rid, 1])
        else:
            benign_edges.append([cid, rid, 0])

    # for edge in ss_edges:
    #     rid1 = edge[0]
    #     rid2 = edge[1]
    #     if '%%%' in str(rid1):
    #         rid1 = int(rid1.split('%%%')[0])
    #     if '%%%' in str(rid2):
    #         rid2 = int(rid2.split('%%%')[0])
    #     if id_user[rid1] in follower_spammers and id_user[rid2] in follower_spammers:
    #         spam_edges.append([rid1, rid2, 1])
    #     else:
    #         benign_edges.append([rid1, rid2, 0])

    for spam_edge in spam_edges:
        # weight or color
        B.add_edge(spam_edge[0], spam_edge[1])
    # B.add_edges_from(spam_edges, color='red')  # format: [user, user]
    for b_edge in benign_edges:
        B.add_edge(b_edge[0], b_edge[1])
    # B.add_edges_from(benign_edges, color='blue')  # format: [user, user]
    log_file.write('***Construct graph B and add edges to it.\n')

    # analyze degree
    review_degree = dict()
    for reviewer, degree in B.degree():
        if reviewer not in review_nodes.keys():
            continue
        else:
            review_degree[reviewer] = degree

    nx.draw_circular(B)
    # nx.draw(B, pos=nx.random_layout(B))
    # nx.draw(B, pos=nx.shell_layout(B))
    # nx.draw(B, pos=nx.spring_layout(B))
    nx.draw(B, pos=nx.spectral_layout(B))
    # bottom_nodes, top_nodes = bipartite.sets(B)
    print('Is bipartite: ', nx.is_bipartite(B))  # cause there are edges between followers
    print('Is connected: ', nx.is_connected(B))
    plt.show()

    log_file.close()
