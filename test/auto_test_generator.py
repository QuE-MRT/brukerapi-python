from brukerapi.folders import Folder
import json
import numpy as np
import pkg_resources

API_VERSION = pkg_resources.get_distribution("brukerapi").version
SUITES=['test_io', 'test_ra']


def test_generator(path_folder, path_config, suites=None):
    if suites:
        if isinstance(suites, str):
            suites = [suites]
    else:
        suites = SUITES

    tests = {}
    for suite in suites:
        tests[suite] = {}

    folder = Folder(path_folder)

    for dataset in folder.dataset_list_rec:
        if dataset.type == 'fid':
            name = 'FID_{}'.format(dataset.path.parents[0].name)
        elif dataset.type == '2dseq':
            name = '2DSEQ_{}_{}'.format(dataset.path.parents[2].name, dataset.path.parents[0].name)

        if 'test_io' in suites:
            tests['test_io'][name] = gen_test_io(dataset, folder.path, name)

        if 'test_ra' in suites:
            tests['test_ra'][name] = gen_test_ra(dataset, folder.path, name)

    with open(path_config, 'w') as json_file:
        json.dump(tests, json_file, indent=4)


def gen_test_io(dataset, abs_path, name):
    """Generate configuration entry for a input/output functionality of an interface

    :param dataset:
    :return:
    """
    print('Generating IO tests for: {} data set'.format(name))

    with dataset as d:
        return d.to_dict(abs_path=abs_path)

def gen_test_ra(dataset, abs_path, name):

    print('Generating RA tests for: {} data set'.format(name))
    test = {}
    slices = []
    with dataset as d:
        test['path'] = str(d.path.relative_to(abs_path))
        slc = tuple(['slice(None)' for _ in range(d.encoded_dim)])

        # single index
        slices.append(
            slc + tuple([int(np.random.random_integers(0,d.shape[i]-1)) for i in range(len(d.shape[d.encoded_dim:]))])
        )

        # slice
        ranges = []

        #generate slices
        for i in range(d.encoded_dim, len(d.shape)):
            if d.shape[i]>1:
                start = int(np.random.random_integers(0,d.shape[i]-2))
                stop = int(np.random.random_integers(start+1,d.shape[i]-1))
                ranges.append('slice({},{})'.format(start, stop))
            else:
                ranges.append('0')

        slices.append(slc+tuple(ranges))

    test['slices'] = slices

    return test