#!/usr/bin/env python3

import argparse
import io
import json
import os
import requests
import urllib.parse
import sys
from base64 import b64encode
from dotenv import load_dotenv
from pathlib import Path
from requests.exceptions import HTTPError
from tqdm import tqdm
from urllib3.connection import NewConnectionError


HOME = Path(__file__).parent.absolute()

PROJECT = None
REF = None
FILE = None


try:
    load_dotenv()

    GIT_HOST = os.environ['GIT_HOST']
    GIT_TOKEN = os.environ['GIT_TOKEN']
    GIT_USER = os.environ['GIT_USER']
    GIT_PWD = os.environ['GIT_PWD']

    b64 = b64encode(f'{GIT_USER}:{GIT_PWD}'.encode("UTF-8")).decode("ascii")
    BASIC_AUTH = f'Basic {b64}'

except KeyError as ex:
    print(f'Please setup required env variable: {str(ex)}')
    sys.exit(1)


def cli():
    global PROJECT
    global FILE
    global REF

    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Project Path, ex: ironos/ironos-release/project")
    parser.add_argument("ref", help="Branch, tag or commit")
    parser.add_argument("file", help="File Path, ex: squashfs.img")

    args = parser.parse_args()

    PROJECT = args.project
    FILE = args.file
    REF = args.ref


def request(path, method='GET', header=None, req_data=None, timeout=30):
    if method not in ['GET', 'POST', 'PATCH', 'DELETE']:
        raise RuntimeError(f'Unsupport method: {method}')

    params = {
        'method': method,
        'url': path,
        'headers': header,
        'timeout': timeout,
        'verify': False
    }

    if req_data:
        params.update({'json': req_data})

    try:
        resp = requests.request(**params)

        resp.raise_for_status()
        return resp

    except (NewConnectionError, ConnectionError) as ex:
        raise RuntimeError(f'Connection failed: {type(ex).__name__}')

    except HTTPError as ex:
        status = ex.response.status_code
        if 400 <= status < 500:
            raise RuntimeError(f'Client Error: {str(ex)}')
        elif 500 <= status < 600:
            raise RuntimeError(f'Server Error: {str(ex)}')

    except Exception as ex:
        raise RuntimeError(ex)


def get_lfs_meta():
    print('Get meta-data')

    header = {
        "PRIVATE-TOKEN": GIT_TOKEN
    }

    path = f'http://{GIT_HOST}/api/v4/projects/{urllib.parse.quote_plus(PROJECT)}/repository/files/{FILE}/raw?ref={REF}'

    resp = request(path, header=header)

    resp_buf = io.StringIO(resp.text)
    for _ in resp_buf:
        if _.startswith("oid"):
            oid = _.strip().split(':')[1]
        elif _.startswith("size"):
            size = _.strip().split()[1]

    #print(f'\t{oid=}, {size=}')

    return oid, size


def get_lfs_downloand_info(oid, size):
    print('Get download info')

    req_data = {
        "operation": "download",
        "objects": [
            {
                "oid": oid,
                "size": int(size)
            }
        ],
         "transfers": [
            "lfs-standalone-file",
            "basic"
        ],
        "ref": {
            "name": REF
        }
    }

    path = f'http://{GIT_HOST}/{PROJECT}.git/info/lfs/objects/batch'

    header = {
        "Authorization": BASIC_AUTH,
        "Content-Type": "application/json"
    }

    resp = request(path, method='POST', header=header, req_data=req_data)
    data = resp.json()

    obj = data['objects'][0]
    href = obj['actions']['download']['href']
    header = obj['actions']['download']['header']

    return href, header


def dl_target_file(url, header, output):
    print('Download file')

    with requests.get(url, headers=header, stream=True) as r:
        r.raise_for_status()

        chunk_size=1024
        num_bars = int(int(r.headers['Content-Length']) / chunk_size)

        with open(output, 'wb') as f:
            for chunk in tqdm(
                r.iter_content(chunk_size=chunk_size),
                total = num_bars,
                unit = 'KB',
                desc = str(output),
                leave = True
            ):
                f.write(chunk)


try:
    cli()

    oid, size = get_lfs_meta()

    href, header = get_lfs_downloand_info(oid, size)

    output = HOME / Path(FILE.rsplit('/')[-1])

    dl_target_file(href, header, output)

except Exception as ex:
    print(f'Unexpected Error: {str(ex)}')
