#!/usr/bin/python
import urllib2
import sys
from collections import namedtuple
from os.path import exists, join, abspath, dirname, basename
from os import makedirs
from subprocess import check_output

from atb_api import API
ATB_API = API(api_format='yaml')

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

Repository = namedtuple('Repository', 'name, search_kwargs')

REPOSITORIES = [
    #Repository('lipids', {'moltype': 'lipid'}),
    Repository('mobley', {'tag': 'Mobley et al.'}),
]

def path_for_repository(repository):
    return join(MOP_DIR, DATA_DIR, repository.name)

def construct_repository(repository):
    repository_path = path_for_repository(repository)
    if not exists(repository_path):
        makedirs(repository_path)
    else:
        raise Exception('Repository already exists at "{0}". Aborting ...'.format(repository_path))

    molecules = ATB_API.Molecules.search(**repository.search_kwargs)
    print 'Will download {0} molecules for repository {1}'.format(
        len(molecules),
        repository.name,
    )
    [
        download_molecule_files_in(molecule, repository_path)
        for molecule in molecules
    ]

if __name__ == "__main__":
    [construct_repository(repository) for repository in REPOSITORIES]
