from sklearn.cluster import KMeans
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
K = 10

base_path = r'E://reviewData//Kingston//'
cluster_path = base_path + r'cluster_results_kmeans.txt'
blob_path = base_path + r'blobs_kmeans.txt'
cluster_center_path = base_path + r'cluster_centers_kmeans.txt'
all_review_path = base_path + r'all_reviews.txt'
vector_path = base_path + r'review_vector.csv'

pure_reviews = []
with open(all_review_path) as rf:
    for line in rf:
        pure_reviews.append(line.strip())

assdf = pd.read_csv(vector_path, encoding='ansi')
X = assdf.values

mds = []
# try to find the most appropriate value for k using elbow method
# for k in range(1, K):
#     model = KMeans(n_clusters=k)
#     model.fit(assdf)
#     md = model.inertia_ / assdf.shape[0]
#     mds.append(md)
#     print('k = {0}, md = {1}'.format(k, md))
# plt.plot(range(1, K), mds)
# plt.show()

# try to find the most appropriate value for kSilhouette Coefficient
# for k in range(1, K):
#     model = KMeans(n_clusters=k)
#     model.fit(assdf)
#     md = model.inertia_ / assdf.shape[0]
#     mds.append(md)
#     print('k = {0}, md = {1}'.format(k, md))
#     s = silhouette_score(vector_points, model.labels_)

clustering = KMeans(n_clusters=5)
clustering.fit(X)

print('clustering.labels_ ', clustering.labels_)
with open(cluster_center_path, 'w') as ccf:
    for center in clustering.cluster_centers_:
        ccf.write(str(center))
        ccf.write('\n')

# write into cluster_result file
with open(cluster_path, 'w') as cp:
    for label in clustering.labels_:
        cp.write(str(label))
        cp.write('\n')

blob_count = max(clustering.labels_)
print('blob_count: ', blob_count)

print('len of clustering.labels_', len(clustering.labels_))
print('pure review count: ', len(pure_reviews))
blobs = dict()
for blob_no in range(blob_count):
    blobs[blob_no] = []
    for review_no, label in enumerate(clustering.labels_):
        if blob_no == label:
            try:
                review_content = pure_reviews[review_no]
                blobs[blob_no].append(review_content)
            except IndexError as ie:
                print('review_no', review_no)
print('blobs', blobs)

# blobs and their member reviews
with open(blob_path, 'w') as bf:
    for key, reviews in blobs.items():
        bf.write('*'*150)
        bf.write('\n')
        bf.write(str(key))
        bf.write(': ')
        for review in reviews:
            bf.write(str(review))
        bf.write('\n')