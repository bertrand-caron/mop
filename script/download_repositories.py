#!/usr/bin/python
import urllib2
import sys
from collections import namedtuple
from os.path import exists, join, abspath, dirname, basename
from os import makedirs
from subprocess import check_output
from glob import glob
from json import loads
from itertools import count
from time import sleep
from multiprocessing import Pool
from functools import partial

from atb_api import API, HTTPError
ATB_API = API(api_format='yaml', debug=True)

DEBUG = False

MOP_DIR = dirname(dirname(abspath(__file__)))
DATA_DIR = 'data/fragments'

def path_for(molecule_id, repository_directory, extension):
    return join(repository_directory, "{0}.{1}".format(molecule_id, extension))

def write_lgf_for(molecule_id, repository_directory):
    stdout = check_output(
        '{bin_dir}/atb2lgf -mtb {mtb_path} -pdb {pdb_path} > {lgf_path}'.format(
            bin_dir=join(MOP_DIR, 'build'),
            mtb_path=path_for(molecule_id, repository_directory, 'mtb'),
            pdb_path=path_for(molecule_id, repository_directory, 'pdb'),
            lgf_path=path_for(molecule_id, repository_directory, 'lgf'),
        ),
        shell=True,
    )

def download_molecule_files_in(repository_directory, molecule_id, debug=DEBUG, maximum_retries = 1):
    print 'INFO: Generating molecule {0}'.format(molecule_id)
    try:
        ATB_API.Molecules.generate_mol_data(molid=molecule_id)

        ATB_API.Molecules.download_file(
            molid=molecule_id,
            atb_format='mtb_aa',
            fnme=path_for(molecule_id, repository_directory, 'mtb'),
        )

        ATB_API.Molecules.download_file(
            molid=molecule_id,
            atb_format='pdb_aa',
            fnme=path_for(molecule_id, repository_directory, 'pdb'),
        )

        write_lgf_for(molecule_id, repository_directory)
    except KeyboardInterrupt:
        raise
    except HTTPError:
        if maximum_retries > 0:
            # Sleep for an hour to allow backup to proceed
            #sleep(3600)
            download_molecule_files_in(molecule_id, repository_directory, debug=debug, maximum_retries=maximum_retries - 1)
        else:
            raise
    except:
        from traceback import format_exc
        print \
'''ERROR:
Traceback:
{0}

Molecule_id:
{1}

'''.format(format_exc(), molecule_id)

Repository = namedtuple('Repository', 'name, search_kwargs, extra_molids')

REPOSITORIES = [
    #Repository('lipids', {'moltype': 'lipid'}, []),
    #Repository('mobley', {'tag': 'Mobley et al.'}, []),
    #Repository('qm2', {'maximum_qm_level': '2', 'is_finished': 'True'}, []),
    #Repository('qm1', {'maximum_qm_level': '1', 'is_finished': 'True'}, []),
    #Repository('has_TI', {'has_TI': True, 'limit': 100000}, [])
    #Repository('warfarins', None, [2202, 2220, 2221, 2222, 2223, 5523, 2225, 5568, 2227, 2228, 5582, 5583, 4450, 4451, 2233, 2234, 4386, 2236, 2237, 4388]),
    #Repository('has_TI_no_duplicates', None, loads(open('has_TI_no_duplicates.json').read())['molids'])
    Repository('qm_1_and_2_21-07-17', {'maximum_qm_level': '1, 2', 'is_finished': 'True'}, [])
]

def path_for_repository(repository):
    return join(MOP_DIR, DATA_DIR, repository.name)

def construct_repository(repository):
    repository_path = path_for_repository(repository)
    if not exists(repository_path):
        makedirs(repository_path)

    if repository.search_kwargs is not None:
        molecule_ids = ATB_API.Molecules.search(limit=100000000, return_type='molids', **repository.search_kwargs)
        print 'Will download {0} molecules for repository {1}: {2}'.format(
            len(molecule_ids),
            repository.name,
            str(molecule_ids)[:100] + '...',
        )
    else:
        molecule_ids = []

    molecule_ids += repository.extra_molids

    found_molids = set([
        int(basename(fullpath.split('.')[0]))
        for fullpath in glob(join(repository_path, '*.lgf'))
    ])

    if False:
        [
            download_molecule_files_in(repository_path, molecule_id)
            for molecule_id in molecule_ids
            if molecule_id not in found_molids
        ]
    else:
        p = Pool(8)

        p.map(
            partial(download_molecule_files_in, repository_path),
            filter(lambda molecule_id: molecule_id not in found_molids, molecule_ids),
        )

if __name__ == "__main__":
    [
        construct_repository(repository)
        for repository in REPOSITORIES
    ]
