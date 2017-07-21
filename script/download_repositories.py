#!/usr/bin/python
import urllib2
import sys
from collections import namedtuple
from os.path import exists, join, abspath, dirname, basename
from os import makedirs
from subprocess import check_output
from glob import glob
from json import loads

from atb_api import API
ATB_API = API(api_format='yaml', debug=True)

DEBUG = False

MOP_DIR = dirname(dirname(abspath(__file__)))
DATA_DIR = 'data/fragments'

def path_for(molecule, repository_directory, extension):
    return join(repository_directory, "{0}.{1}".format(molecule.molid, extension))

def write_lgf_for(molecule, repository_directory):
    stdout = check_output(
        '{bin_dir}/atb2lgf -mtb {mtb_path} -pdb {pdb_path} > {lgf_path}'.format(
            bin_dir=join(MOP_DIR, 'build'),
            mtb_path=path_for(molecule, repository_directory, 'mtb'),
            pdb_path=path_for(molecule, repository_directory, 'pdb'),
            lgf_path=path_for(molecule, repository_directory, 'lgf'),
        ),
        shell=True,
    )

def download_molecule_files_in(molecule, repository_directory, debug=DEBUG):
    print 'INFO: Generating molecule {0}'.format(molecule.molid)
    try:
        molecule.generate_mol_data()

        molecule.download_file(
            atb_format='mtb_aa',
            fnme=path_for(molecule, repository_directory, 'mtb'),
        )

        molecule.download_file(
            atb_format='pdb_aa',
            fnme=path_for(molecule, repository_directory, 'pdb'),
        )

        write_lgf_for(molecule, repository_directory)
    except KeyboardInterrupt:
        raise
    except:
        from traceback import format_exc
        print \
'''ERROR:
Traceback:
{0}

Molecule:
{1}

'''.format(format_exc(), molecule)

Repository = namedtuple('Repository', 'name, search_kwargs, extra_molids')

REPOSITORIES = [
    #Repository('lipids', {'moltype': 'lipid'}, []),
    #Repository('mobley', {'tag': 'Mobley et al.'}, []),
    #Repository('qm2', {'maximum_qm_level': '2', 'is_finished': 'True'}, []),
    #Repository('qm1', {'maximum_qm_level': '1', 'is_finished': 'True'}, []),
    #Repository('has_TI', {'has_TI': True, 'limit': 100000}, [])
    Repository('warfarins', None, [2202, 2220, 2221, 2222, 2223, 5523, 2225, 5568, 2227, 2228, 5582, 5583, 4450, 4451, 2233, 2234, 4386, 2236, 2237, 4388]),
    Repository('has_TI_no_duplicates', None, loads(open('has_TI_no_duplicates.json').read())['molids'])
]

def path_for_repository(repository):
    return join(MOP_DIR, DATA_DIR, repository.name)

def construct_repository(repository):
    repository_path = path_for_repository(repository)
    if not exists(repository_path):
        makedirs(repository_path)

    if repository.search_kwargs is not None:
        molecules = ATB_API.Molecules.search(limit=1000000, **repository.search_kwargs)
        print 'Will download {0} molecules for repository {1}: {2}'.format(
            len(molecules),
            repository.name,
            str(molecules)[:100] + '...',
        )
    else:
        molecules = []

    molecules += ATB_API.Molecules.molids(molids=repository.extra_molids)
    print(molecules)

    found_molids = set([
        int(basename(fullpath.split('.')[0]))
        for fullpath in glob(join(repository_path, '*.lgf'))
    ])

    [
        download_molecule_files_in(molecule, repository_path)
        for molecule in molecules
        if molecule.molid not in found_molids
    ]

if __name__ == "__main__":
    [
        construct_repository(repository)
        for repository in REPOSITORIES
    ]
