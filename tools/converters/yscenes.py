#! /usr/bin/env python3 -B

# This is just a hacky utility to convert scenes from various format.

import click, glob, os

def get_filenames(dirname, sceneglob, fileglob):
    excluded = []
    if os.path.exists(f'{dirname}/excluded.txt'):
        with open(f'{dirname}/excluded.txt') as f:
            excluded = [ f'{dirname}/' + l.strip() for l in f.readlines() ]
    filenames = []
    for filename in sorted(glob.glob(f'{dirname}/{sceneglob}/{fileglob}')):
        is_excluded = False
        for exc in excluded:
            if exc in filename:
                is_excluded = True
        if is_excluded:
            print(f'exclude {filename}')
        else:                    
            filenames += [ filename ]
    return filenames

def run_cmd(cmd):
    print(f'>>> {cmd}')
    os.system(cmd)

@click.group()
def run():
    pass

@run.command()
@click.argument('dirname', required=True)
@click.argument('scene', required=False, default='*')
def convert(dirname, scene):
    tungsten = dirname in ['bitterli']
    pbrt = dirname in ['bitterli_pbrt']
    ext = 'json' if tungsten else 'pbrt'
    for filename in get_filenames(f'{dirname}/original', scene, f'*.{ext}'):
        srcdir = os.path.dirname(filename)
        outdir = srcdir.replace('original','yocto')
        if os.path.exists(outdir):
            run_cmd(f'rm -rf {outdir} && mkdir -p {outdir}')
    for filename in get_filenames(f'{dirname}/original', scene, f'*.{ext}'):
        srcdir = os.path.dirname(filename)
        basename = os.path.basename(filename)
        outdir = srcdir.replace('original','yocto')
        outname = basename.replace('.'+ext,'.obj')
        if tungsten:
            run_cmd(f'../yocto-gl/bin/ytungsten {srcdir}/{basename} -o {outdir}/{outname}')
        if pbrt:
            run_cmd(f'../yocto-gl/bin/ypbrt {srcdir}/{basename} -o {outdir}/{outname}')
        if os.path.exists(f'{srcdir}/textures'):
            run_cmd(f'cp -r {srcdir}/textures {outdir}/')
        if os.path.exists(f'{srcdir}/LICENSE.txt'):
            run_cmd(f'cp -r {srcdir}/LICENSE.txt {outdir}/')

@run.command()
@click.argument('dirname', required=True)
@click.argument('scene', required=False, default='*')
def view(dirname, scene='*'):
    for filename in get_filenames(f'{dirname}/yocto', scene, f'*.obj'):
        run_cmd(f'../yocto-gl/bin/yview -D --eyelight {filename}')

@run.command()
@click.argument('dirname', required=True)
@click.argument('scene', required=False, default='*')
def trace(dirname, scene='*'):
    for filename in get_filenames(f'{dirname}/yocto', scene, f'*.obj'):
        run_cmd(f'../yocto-gl/bin/yitrace -D {filename}')

@run.command()
@click.argument('dirname', required=True)
@click.option('--resolution', '-r', default=256, type=int)
@click.option('--samples', '-s', default=64, type=int)
@click.argument('scene', required=False, default='*')
def render(dirname, scene='*',samples=16,resolution=256):
    for filename in get_filenames(f'{dirname}/yocto', scene, f'*.obj'):
        run_cmd(f'../yocto-gl/bin/ytrace -D -r {resolution} -s {samples} {filename}')

@run.command()
def sync():
    os.system('rsync -avc --delete ./ ../yocto-scenes')


if __name__ == '__main__':
    run()