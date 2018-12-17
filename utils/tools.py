from utils import dumper, finder, tf_generator
from os.path import join, exists
import matplotlib.pyplot as plt
from utils import config
from glob2 import glob
import numpy as np
import pickle
import sys
import cv2

LABELS = dumper.label_loader(dir_=config.DATA_DIR)


def write(s, condition=True):
    if condition:
        sys.stdout.write(s)
        sys.stdout.write("\n")
        sys.stdout.flush()


def dict_of_all_classes() -> dict:
    dumped = join(dumper.DUMP_DIR, "dict_of_classes.pickle")
    if exists(dumped):
        classes = pickle.load(open(dumped, "rb"))
    else:
        raw = list(set([i[0] for i in LABELS.itertuples()]))
        classes = {}
        for i, j in enumerate(raw):
            fnd = finder.Finder(subject=j, etc=True, resource=config.RESOURCE, just_count_images=True)
            result = sorted(list(fnd.search_result))
            if not len(result) == 1:
                classes.update({j: result})
        pickle.dump(classes, open(dumped, "wb"))
    return classes


def mid_to_string(mid_or_name) -> str:
    if mid_or_name.startswith('/m'):
        selected = LABELS.loc[LABELS['code'] == mid_or_name]
        selected = selected.to_dict()
        return list(selected['code'].keys())[0]
    else:
        selected = LABELS.loc[mid_or_name]
        selected = selected.to_dict()
        return selected['code']


def draw(img, bboxes, thickness):
    bboxes = bboxes.astype(np.uint)
    for b in bboxes:
        img = cv2.rectangle(img=img, pt1=(b[0], b[1]), pt2=(b[2], b[3]), color=(0, 0, 255), thickness=thickness)
    return img


def generate(csv_input, output_path, images_dir, classes):
    tf_generator.main(csv_input=csv_input, output_path=output_path, images_dir=images_dir, classes=classes)


def bbox_test(address, target, n=2, thickness=3):
    target = target.title()
    file = "{}_bbox.csv".format(target.title())
    csv = np.genfromtxt("{}/{}/{}".format(address, "records", file), delimiter=",", skip_header=1, dtype=str)
    dir_ = join(address, "images", target)
    images = glob("{}/*.jpg".format(dir_))
    selected = np.random.choice(images, n*n, replace=False)
    del images, dir_

    plt.figure(figsize=(15, 10))
    for idx, img_dir in enumerate(selected, start=1):
        img = plt.imread(img_dir)
        res = csv[np.where(csv[:, config.IMG] == img_dir.rsplit("/")[-1])]
        bboxes = res[:, config.BBOX_SLICE]
        titles, counts = np.unique(res[:, config.LABEL], return_counts=True)
        plt.subplot(n, n, idx)
        img = draw(img, bboxes, thickness)
        plt.imshow(img)
        title = ""
        for i, j in zip(counts, titles):
            title += "{} {}, ".format(i, j)
        plt.title(title)
        plt.axis('off')
    plt.show()


if __name__ == "__main__":
    # print(dict_of_all_classes())
    pass
