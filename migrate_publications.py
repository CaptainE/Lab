#!/usr/bin/env python
"""
Migrate publication list from SE3 website here
Note: this script will overwrite current yml file
Usage:
step 1: download the publication from wordpress in bibtex(.bib) format
step 2: execute below command with the correct path to the downloaded file:
  python migrate_publications.py --bib-path "/Users/menglin/Projects/website_conctribution/teachpress_pub_23092021.bib"
"""
import argparse
import yaml


def _extract(line):
    key = line.split(" ")[0]
    if key == "year":
        prefix = key + "  = {"
    else:
        prefix = key + " = {"
    value = line.split(prefix)[-1].split("},")[0]
    return key, value


def parse_bibtex(args):
    # get a list of publication dict
    # - title: How Kondo-holes create intense nanoscale heavy-fermion hybridization disorder
  # image: dummy.png
  # description: ""
  # authors: MH Hamidian, AR Schmidt, IA Firmo, MP Allan, P Bradley, JD Garrett, TJ Williams, GM Luke, Y Dubi, AV Balatsky, JC Davis
  # link:
  #   url: http://www.pnas.org/content/108/45/18233
  #   display:  PNAS 108, 18233 (2011)
  # highlight: 0
  # news2:
    print("Step 1: Reading publications from {}".format(args.bib_path))

    with open(args.bib_path, "r") as f:
        lines = f.readlines()
    pub_list = []  # a list of dict
    pub_venue = set()
    pub_years = []

    previous_l = ""
    for line in lines:
        line = line.strip()
        if line.startswith("%") or len(line.strip()) == 0:
            continue

        if line.startswith("@"):
            # initialize a new dict
            pub_dict = {}
            pub_dict["ref"] = line.split("{")[-1].split(",")[0]
            pub_venue.add(line.split("@")[-1].split("{")[0])
        elif line.startswith("}"):
            pub_list.append(pub_dict)

        elif not line.endswith("},") and not line.startswith("keywords"):
            # which means this line is not finished
            previous_l = line
        else:
            # title, author, url, year, date, booktitle, address, note, and keywords
            # {'inproceedings', 'techreport', 'phdthesis', 'book', 'incollection', 'article', 'inbook', 'mastersthesis', 'conference'}
            if not line.endswith("},"):
                line = line + ","
            k, v = _extract(previous_l + line)
            previous_l = ""

            if k == "url":
                # TODO: may need to update url to other domain?
                pub_dict["link"] = {"url": v, "display": "PDF"}
            elif k == "author":
                v = v.replace("{", "")
                v = v.replace("}", "")
                v = v.replace("*", "\*")  # to properly disply * in markdown
                pub_dict[k] = v.replace(" and", ",")
            elif k == "note":
                pub_dict[k] = ", (" + v + ")"
            elif k == "abstract":
                continue
            elif k == "year":
                pub_years.append(v)
                pub_dict[k] = v
            else:
                pub_dict[k] = v

    print("...parsed {} publications".format(len(pub_list)))
    print(pub_venue)
    pub_years = sorted(list(set(pub_years)), reverse=True)
    return pub_list, pub_years


def write_yaml(pub_list, pub_years):
    yml_path = "_data/publist.yml"

    with open(yml_path, 'w') as file:
        yaml.dump(pub_list, file)
    print("Step 2.1: written to {}".format(yml_path))

    yml_path = "_data/pubyears.yml"

    with open(yml_path, 'w') as file:
        yaml.dump(pub_years, file)
    print("Step 2.2: written to {}".format(yml_path))


def main():
    parser = argparse.ArgumentParser(description='Publication migration parser')
    parser.add_argument('--bib-path', default="", type=str,
                        help='Path to the txt file downloaded from SE3 website')
    args = parser.parse_args()

    pub_list, pub_years = parse_bibtex(args)
    write_yaml(pub_list, pub_years)


if __name__ == '__main__':
    main()
