import subprocess
import sys

from collections import namedtuple


def pad_list(items, pad_to=10, pad_with=''):
    if len(items) >= pad_to:
        return items

    return items + [pad_with for i in range(0, pad_to - len(items))]


def namedtuplify(headers, rows):
    max_cols = len(headers)
    Row = namedtuple(
        'Row',
        [col_name.replace(' ', '') for col_name in headers]
    )
    rows = [Row(*pad_list(row, pad_to=max_cols)) for row in rows]

    return rows


def get_docker_ps():
    output = [
        [i.strip() for i in line.split('  ') if i.strip()]
        for line in subprocess.check_output(
            ['docker', 'ps', '-a'],
            encoding='utf-8'
        ).splitlines()
    ]
    headers, rows = output[0], output[1:]

    return namedtuplify(headers, rows)


def get_docker_images():
    output = [
        [i.strip() for i in line.split('  ') if i.strip()]
        for line in subprocess.check_output(
            ['docker', 'images'],
            encoding='ascii'
        ).splitlines()
    ]
    headers, rows = output[0], output[1:]

    return namedtuplify(headers, rows)


def untagged_containers(rows=None):
    "List of container ids using untagged images"
    rows = rows or get_docker_ps()

    return [
        row.CONTAINERID
        for row in rows if row.STATUS == 'Created'
    ]


def untagged_images(rows=None):
    "List of image ids that are not tagged"
    rows = rows or get_docker_images()

    return [
        row.IMAGEID
        for row in rows if row.REPOSITORY == '<none>' or row.TAG == '<none>'
    ]


if __name__ == '__main__':
    container_ids = untagged_containers()
    image_ids = untagged_images()

    print(image_ids)

    if not image_ids and not container_ids:
        print("Nothing to cleanup!")
        sys.exit()

    if container_ids:
        print("Removing containers using untagged images...")
        for container_id in container_ids:
            try:
                output = subprocess.check_output(
                    ['docker', 'rm', '-f', container_id]
                )
            except subprocess.CalledProcessError as e:
                print(e)
                sys.exit()
            print(output)

    if image_ids:
        print("Removing untagged images...")
        for image_id in image_ids:
            try:
                output = subprocess.check_output(['docker', 'rmi', image_id])
            except subprocess.CalledProcessError as e:
                print(e)
                sys.exit()
            print(output)

    print("Done !!! 🐳 🐳 🐳")
