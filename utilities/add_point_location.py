#!/usr/bin/env python3
"""
This is used to add point locations to a CSV file. This utility exists to maintain proper indexing, formatting, and coordinate precision.
"""
import sys
import os
import argparse
import pandas as pd
import numpy as np
from shutil import copyfile

postal_di = {
    "AK": "Alaska",
    "AB": "Alberta",
    "BC": "British Columbia",
    "MB": "Manitoba",
    "SK": "Saskatchewan",
    "YT": "Yukon",
    "NT": "Northwest Territories",
}


def cmdline_args():
    # Make parser object
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "name",
        type=str,
        help="Primary name of point location. Required.",
    )
    p.add_argument(
        "region",
        type=str,
        choices=["AB", "AK", "BC", "MB", "SK", "NT", "YT"],
        help="Region postal code of point location. Required.",
    )
    p.add_argument(
        "country",
        type=str,
        choices=["CA", "US"],
        help="Country abbreviation of the point location. Required.",
    )
    p.add_argument(
        "latitude",
        type=float,
        help="Latitude of the point location. Required.",
    )
    p.add_argument(
        "longitude",
        type=float,
        help="Longitude of the point location. Required.",
    )
    p.add_argument(
        "--optional_name",
        type=str,
        help="Secondary or alternate name of point location. Optional.",
    )

    return p.parse_args()


def read_csv_by_region(region):
    point_dir = "../vector_data/point"
    suffix = "_point_locations.csv"
    fname = postal_di[region].replace(" ", "_").lower() + suffix
    csv_path = os.path.join(point_dir, fname)
    df = pd.read_csv(csv_path)
    return df, csv_path


def get_last_id_number_in_df(df):
    """Fetch numeric part of the current greatest id value."""
    last_id_number = max([int(x[2:]) for x in df.id.values])
    return last_id_number


def create_new_id(region, last_id_number):
    """Create a new unique id for the record to be added."""
    new_id = region + str(last_id_number + 1)
    return new_id


def create_new_record(new_id, name, region, country, lat, lon, alt_name):
    """Create the new point location from user input.
    A defualt value of 0 will be added for the coastal distance which can
    then be computed later."""
    if alt_name == None:
        alt_name = np.nan
    record = [new_id, name, alt_name, postal_di[region], country, lat, lon, 0]
    return record


def insert_new_record(df, record):
    """Insert new record at end of DataFrame."""
    row = pd.Series(record, index=df.columns)
    new_df = df.append(row, ignore_index=True)
    new_df = new_df.round(4)
    return new_df


def sort_alphabetically(new_df):
    """Sort dataframe alphabetically by location name."""
    new_df.sort_values("name", inplace=True)
    return new_df


def show_diff(df, new_df):
    print(os.linesep)
    print("The difference between the old and new file will be:")
    diff_df = pd.merge(df, new_df, how="outer", indicator="Exist")
    diff_df = diff_df.loc[diff_df["Exist"] != "both"]
    del diff_df["Exist"]
    print(diff_df)


def write_new_csv(new_df, csv_path):
    """This will create a copy of the existing unmodified csv with a 'deprecated' suffix prior to over-writing that data file with the same name. If the deprecated file exists, it will be overwritten. Deprecated fiels will not be tracked."""
    dst = csv_path.replace(".csv", "_DEPRECATED.csv")
    copyfile(csv_path, dst)
    new_df.to_csv(csv_path, index=False)
    print("New file written to", csv_path)


def yes_no(answer):
    """Helper function to prompt user to create a new file or not."""
    yes = set(["yes", "y", "ye", ""])
    no = set(["no", "n"])

    while True:
        choice = input(answer).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no'")


if __name__ == "__main__":
    try:
        args = cmdline_args()
        df, csv_path = read_csv_by_region(args.region)
        last_id = get_last_id_number_in_df(df)
        new_id = create_new_id(args.region, last_id)
        record = create_new_record(
            new_id,
            args.name,
            args.region,
            args.country,
            args.latitude,
            args.longitude,
            args.optional_name,
        )
        new_df = insert_new_record(df, record)
        new_df = sort_alphabetically(new_df)
        show_diff(df, new_df)
        create = yes_no("Do you wish to proceed with creating the new file (y/n)?")
        if create:
            write_new_csv(new_df, csv_path)
        else:
            print("No new file was created. Program exiting.")
    except:
        print(
            "Try python add_point_location.py 'Vanta' 'AK' 'US' 99.9999 -99.9999 --optional_name='Bubba'"
        )
