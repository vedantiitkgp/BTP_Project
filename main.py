#! /usr/bin/env python3

import argparse
from scraper import CollectPosts
from settings import EMAIL, PASSWORD

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Non API public FB miner')

    parser.add_argument('-p', '--pages', nargs='+',
                        dest="pages",
                        help="List the pages you want to scrape for recent posts")

    parser.add_argument("-g", '--groups', nargs='+',
                        dest="groups",
                        help="List the groups you want to scrape for recent posts")

    parser.add_argument("-d", "--depth", action="store",
                        dest="depth", default=5, type=int,
                        help="How many recent posts you want to gather -- in multiples of (roughly) 8.")
    
    parser.add_argument("-n","--number_post",action="store",
                        dest="number_posts",default=10,type=int,
                        help="How many posts you want to scrape?")
    args = parser.parse_args()

    if not args.groups and not args.pages:
        print("Something went wrong!")
        print(parser.print_help())
        exit()

    if not EMAIL or not PASSWORD:
        raise Exception(
            "EMAIL or password not provided correctly, check your env file.")

    if args.groups:

        C = CollectPosts(ids=args.groups, depth=args.depth,number_posts=args.number_posts)
        C.login(EMAIL, PASSWORD)
        C.collect("groups")

    elif args.pages:
        print("Starting collecting page "+str(args.pages))
        C = CollectPosts(ids=args.pages, depth=args.depth,number_posts=args.number_posts)
        C.login(EMAIL, PASSWORD)
        C.collect("pages")
