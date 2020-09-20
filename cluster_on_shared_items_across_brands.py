# to cluster reviewers via shared items across items/brands
import datetime
import os
import random
import numpy as np
import pandas as pd


def get_random():
    random.seed()
    return random.random()


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


def time_error(times):
    # time like 2020-08-12 20:31
    # log.write(f'#####Calculate time error of {times}.\n')
    print(f'Calculate time error of {times}')
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
            # log.write(f'-----Time error between {time_1} and {time_2} is: {time_diff} days.\n')
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


if __name__ == '__main__':
    result_path = 'result_cluster_on_shared_3_items_across_brands.txt'
    item_reviewers = dict()
    item_sprites = dict()
    all_reviewers = []
    all_followers = []
    reviewer_contents = dict()

    reviewer_data = dict()
    follower_data = dict()

    for py in os.listdir('.'):
        if '_comments.csv' in py:
            item = py.split('_')[0]
            item_reviewers[item] = []
            reviews = pd.read_csv(py, encoding='ansi')
            for index, row in reviews.iterrows():
                reviewer = row['name']
                r_content = row['content']
                r_time = row['time']
                item_reviewers[item].append(reviewer)
                all_reviewers.append(reviewer)
                reviewer_data_key = str(reviewer) + '%%%' + item
                if reviewer_data_key not in reviewer_data.keys():
                    reviewer_data[reviewer_data_key] = [r_content, r_time]
                # else:
                #     print(f'Alert! duplicate reviewer_data_key found! {reviewer_data_key}')
                #     reviewer_data_key = reviewer + '%%%' + item + '###' + str(get_random())
                #     reviewer_data[reviewer_data_key] = [r_content, r_time]

    for py in os.listdir('.'):
        if '_sprites_verbose.csv' in py:
            item = py.split('_')[0]
            item_sprites[item] = []
            reviews = pd.read_csv(py)
            for index, row in reviews.iterrows():
                sprite = row['follower']
                r_content = row['r_content']
                r_time = row['r_time']
                if '自营' in sprite or '旗舰' in sprite:
                    continue
                all_followers.append(sprite)
                item_sprites[item].append(sprite)
                f_content = row['f_content']
                f_time = row['f_time']
                follower_data_key = str(sprite) + '%%%' + item
                if follower_data_key not in follower_data.keys():
                    follower_data[follower_data_key] = [f_content, f_time]
                # else:
                #     print(f'Alert! duplicate follower_data_key found! {follower_data_key}')
                #     follower_data_key = follower + '%%%' + item + '###' + str(get_random())
                #     follower_data[follower_data_key] = [f_content, f_time]

    overlapped_reviewers = set()
    overlapped_sprites = set()

    all_reviewers = list(set(all_reviewers))
    all_followers = list(set(all_followers))

    reviewers_of_duplicate_contents = []
    r_times = []
    # to find reviewers who post 3 or more
    for i1, r1 in item_reviewers.items():
        for i2, r2 in item_reviewers.items():
            for i3, r3 in item_reviewers.items():
                if i1 == i2 or i1 == i3 or i2 == i3:
                    continue
                shared = list(set(r1).intersection(set(r2)).intersection(set(r3)))
                for s in shared:
                    print(f'Found shared reviewers.')
                    overlapped_reviewers.add(s)
                    # to evaluate duplication and burst
                    key1 = str(s) + '%%%' + i1
                    key2 = str(s) + '%%%' + i2
                    key3 = str(s) + '%%%' + i3
                    content1 = reviewer_data[key1][0]
                    content2 = reviewer_data[key2][0]
                    content3 = reviewer_data[key3][0]
                    r_times.append(reviewer_data[key1][1])
                    r_times.append(reviewer_data[key2][1])
                    r_times.append(reviewer_data[key3][1])
                    if content1 == content2 or content1 == content3 or content2 == content3:
                        reviewers_of_duplicate_contents.append(s)
    # time_error_of_reviews = time_error(r_times)
    time_std_of_reviews = time_std(r_times)

    followers_of_duplicate_contents = []
    f_times = []
    # to find responses who post 3 or more
    for i1, s1 in item_sprites.items():
        for i2, s2 in item_sprites.items():
            for i3, s3 in item_sprites.items():
                if i1 == i2 or i1 == i3 or i2 == i3:
                    continue
                shared = list(set(s1).intersection(set(s2)).intersection(set(s3)))
                for s in shared:
                    print(f'Found shared followers.')
                    overlapped_sprites.add(s)
                    # to evaluate duplication and burst
                    key1 = s + '%%%' + i1
                    key2 = s + '%%%' + i2
                    key3 = s + '%%%' + i3
                    content1 = follower_data[key1][0]
                    content2 = follower_data[key2][0]
                    content3 = follower_data[key3][0]
                    f_times.append(follower_data[key1][1])
                    f_times.append(follower_data[key2][1])
                    f_times.append(follower_data[key3][1])
                    if content1 == content2 or content1 == content3 or content2 == content3:
                        followers_of_duplicate_contents.append(s)
    # time_error_of_follows = time_error(f_times)
    time_std_of_follows = time_std(f_times)

    # ratio of overlapped reviewers and followers
    ratio_of_reviewers = len(overlapped_reviewers) / len(all_reviewers)
    ratio_of_followers = len(overlapped_sprites) / len(all_followers)

    ratio_of_reviewers_with_duplicated_contents = len(reviewers_of_duplicate_contents) / len(overlapped_reviewers)
    ratio_of_followers_with_duplicated_contents = len(followers_of_duplicate_contents) / len(overlapped_sprites)

    with open(result_path, 'w') as wf:
        wf.write('Shared reviewers\n')
        wf.write(f'Ratio of overlapped_reviewers: {ratio_of_reviewers}\n')
        wf.write(f'Ratio of overlapped reviewers with duplicated contents posted. '
                 f'{ratio_of_reviewers_with_duplicated_contents}\n')
        wf.write(f'Time std of reviews: {time_std_of_reviews}\n')
        for reviewer in list(overlapped_reviewers):
            wf.write(reviewer + ',')
        wf.write('\nShared sprites\n')
        wf.write(f'Ratio of overlapped_followers: {ratio_of_followers}\n')
        wf.write(f'Ratio of overlapped followers with duplicated contents posted. '
                 f'{ratio_of_followers_with_duplicated_contents}\n')
        wf.write(f'Time std of follows: {time_std_of_follows}\n')
        for sprite in list(overlapped_sprites):
            wf.write(sprite + ',')
